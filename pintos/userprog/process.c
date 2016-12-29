#include "userprog/process.h"
#include <debug.h>
#include <inttypes.h>
#include <round.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <list.h>
#include "userprog/gdt.h"
#include "userprog/pagedir.h"
#include "userprog/tss.h"
#include "userprog/syscall.h"
#include "filesys/directory.h"
#include "filesys/file.h"
#include "filesys/filesys.h"
#include "threads/flags.h"
#include "threads/init.h"
#include "threads/interrupt.h"
#include "threads/palloc.h"
#include "threads/malloc.h"
#include "threads/thread.h"
#include "threads/vaddr.h"
#ifdef VM
#include "vm/page.h"
#include "vm/frame.h"
#endif


static thread_func start_process NO_RETURN;
static bool load (const char *cmdline, void (**eip) (void), void **esp);


/* My Implementation */
/* Shared variables among the threads, used for process_execute. */
struct lock exec_mutex;
struct semaphore exec_wait_load;

/* Mutex that need to acquire when a user process uses file system. */
struct lock filesys_mutex;

bool load_success = false;
/* My Implementation */

/* Starts a new thread running a user program loaded from
   FILENAME.  The new thread may be scheduled (and may even exit)
   before process_execute() returns.  Returns the new process's
   thread id, or TID_ERROR if the thread cannot be created. */
tid_t
process_execute (const char *file_name)
{
  char *fn_copy;
  tid_t tid;
  struct tc_block *tcb;

  /* Make a copy of FILE_NAME.
     Otherwise there's a race between the caller and load(). */
  fn_copy = palloc_get_page (0);
  if (fn_copy == NULL)
    return TID_ERROR;
  strlcpy (fn_copy, file_name, ARG_LIMIT);

  /* My Implementation */
  lock_acquire (&exec_mutex);
  /* My Implementation */

  /* Create a new thread to execute FILE_NAME.
   * tid is set to -1 when it fails to load, only.  */
  tid = thread_create (file_name, PRI_DEFAULT, start_process, fn_copy);

  if (tid != TID_ERROR)
  {
	// Set parent thread in TCB to the current thread.
	tcb = tcb_lookup(tid);
  	ASSERT (tcb != NULL);
  	tcb->parent = thread_current();
  }
  else
  {
	// case when the exec thread fails to load.
	palloc_free_page (fn_copy);
	return tid;
  }

  /* My Implementation */
  // exec thread loaded successfully
  // Now it checks whether the exec thread executed successfully.
  sema_down (&exec_wait_load);
  if (!load_success)
	tid = TID_ERROR;
  lock_release (&exec_mutex);
  /* My Implementation */

  return tid;
}

/* A thread function that loads a user process and makes it start
   running. */
static void
start_process (void *f_name)
{
  char *file_name = f_name;
  struct intr_frame if_;
  bool success;

  /* Initialize interrupt frame and load executable. */
  memset (&if_, 0, sizeof if_);
  if_.gs = if_.fs = if_.es = if_.ds = if_.ss = SEL_UDSEG;
  if_.cs = SEL_UCSEG;
  if_.eflags = FLAG_IF | FLAG_MBS;

  success = load (file_name, &if_.eip, &if_.esp);

  /* My Implementation */
  load_success = success;
  sema_up (&exec_wait_load);
  /* My Implementation */

  /* If load failed, quit. */
  palloc_free_page (file_name);
  if (!success)
    thread_exit ();

  /* Start the user process by simulating a return from an
     interrupt, implemented by intr_exit (in
     threads/intr-stubs.S).  Because intr_exit takes all of its
     arguments on the stack in the form of a `struct intr_frame',
     we just point the stack pointer (%esp) to our stack frame
     and jump to it. */
  asm volatile ("movl %0, %%esp; jmp intr_exit" : : "g" (&if_) : "memory");
  NOT_REACHED ();
}

/* Waits for thread TID to die and returns its exit status.  If
   it was terminated by the kernel (i.e. killed due to an
   exception), returns -1.  If TID is invalid or if it was not a
   child of the calling process, or if process_wait() has already
   been successfully called for the given TID, returns -1
   immediately, without waiting.

   This function will be implemented in problem 2-2.  For now, it
   does nothing. */
int
process_wait (tid_t child_tid)
{
  /* My Implementation */
  struct tc_block *tcb;
  int exit_code;

  if ((tcb = tcb_lookup(child_tid)) == NULL)	// case ; there's no such tcb
	return -1;
  if (tcb->parent != thread_current())			// case ; parent does not match
	return -1;
  sema_down(&tcb->dead);						// wait for the child
  exit_code = tcb->exit_flag ? tcb->exit_code : -1;

  lock_acquire (&tcb_lock);
  hash_delete (&tcb_table, &tcb->hash_elem);
  lock_release (&tcb_lock);

  free(tcb);

  return exit_code;
  /* My Implementation */
}

/* Free the current process's resources. */
void
process_exit (void)
{
  struct thread *curr = thread_current ();
  uint32_t *pd;

  /* My Implementation */
  struct hash *h;
  struct tc_block *tcb;
  struct file *ef;

  /* Supplemental page table */
#ifdef VM
  struct s_page_table *spt;			/* Supplemental page table */
  struct hash *mmap_t;				/* Memory mapping table */
#endif

  /* Set alive flag of TCB to false */
  tcb = tcb_lookup(curr->tid);
  sema_up(&tcb->dead);

  ef = curr->exec_holder;
  if (ef != NULL)
  {
	lock_acquire(&filesys_mutex);
	file_close(ef);
	lock_release(&filesys_mutex);
  }

  /* Free the fd table */
  h = curr->fd_table;
  if (h != NULL)
	hash_destroy (h, delete_fde);
  free(h);

#ifdef VM
  /* Free the table for memory mappings */
  mmap_t = curr->mmap_table;
  if (mmap_t != NULL)
  	hash_destroy (mmap_t, delete_me);
  free(mmap_t);

  /* Free the frames that allocated to that thread. */
  clean_frame(curr);

  /* Free the supplemental page table */
  spt = curr->sp_table;
  if (spt != NULL)
  {
	curr->sp_table = NULL;
	spt_destroy(spt);
  }
#endif

  /* My Implementation */

  /* Destroy the current process's page directory and switch back
     to the kernel-only page directory. */
  pd = curr->pagedir;
  if (pd != NULL)
    {
      /* Correct ordering here is crucial.  We must set
         cur->pagedir to NULL before switching page directories,
         so that a timer interrupt can't switch back to the
         process page directory.  We must activate the base page
         directory before destroying the process's page
         directory, or our active page directory will be one
         that's been freed (and cleared). */
      curr->pagedir = NULL;
      pagedir_activate (NULL);
      pagedir_destroy (pd);
    }
}

/* Sets up the CPU for running user code in the current
   thread.
   This function is called on every context switch. */
void
process_activate (void)
{
  struct thread *t = thread_current ();

  /* Activate thread's page tables. */
  pagedir_activate (t->pagedir);

  /* Set thread's kernel stack for use in processing
     interrupts. */
  tss_update ();
}

/* We load ELF binaries.  The following definitions are taken
   from the ELF specification, [ELF1], more-or-less verbatim.  */

/* ELF types.  See [ELF1] 1-2. */
typedef uint32_t Elf32_Word, Elf32_Addr, Elf32_Off;
typedef uint16_t Elf32_Half;

/* For use with ELF types in printf(). */
#define PE32Wx PRIx32   /* Print Elf32_Word in hexadecimal. */
#define PE32Ax PRIx32   /* Print Elf32_Addr in hexadecimal. */
#define PE32Ox PRIx32   /* Print Elf32_Off in hexadecimal. */
#define PE32Hx PRIx16   /* Print Elf32_Half in hexadecimal. */

/* Executable header.  See [ELF1] 1-4 to 1-8.
   This appears at the very beginning of an ELF binary. */
struct Elf32_Ehdr
  {
    unsigned char e_ident[16];
    Elf32_Half    e_type;
    Elf32_Half    e_machine;
    Elf32_Word    e_version;
    Elf32_Addr    e_entry;
    Elf32_Off     e_phoff;
    Elf32_Off     e_shoff;
    Elf32_Word    e_flags;
    Elf32_Half    e_ehsize;
    Elf32_Half    e_phentsize;
    Elf32_Half    e_phnum;
    Elf32_Half    e_shentsize;
    Elf32_Half    e_shnum;
    Elf32_Half    e_shstrndx;
  };

/* Program header.  See [ELF1] 2-2 to 2-4.
   There are e_phnum of these, starting at file offset e_phoff
   (see [ELF1] 1-6). */
struct Elf32_Phdr
  {
    Elf32_Word p_type;
    Elf32_Off  p_offset;
    Elf32_Addr p_vaddr;
    Elf32_Addr p_paddr;
    Elf32_Word p_filesz;
    Elf32_Word p_memsz;
    Elf32_Word p_flags;
    Elf32_Word p_align;
  };

/* Values for p_type.  See [ELF1] 2-3. */
#define PT_NULL    0            /* Ignore. */
#define PT_LOAD    1            /* Loadable segment. */
#define PT_DYNAMIC 2            /* Dynamic linking info. */
#define PT_INTERP  3            /* Name of dynamic loader. */
#define PT_NOTE    4            /* Auxiliary info. */
#define PT_SHLIB   5            /* Reserved. */
#define PT_PHDR    6            /* Program header table. */
#define PT_STACK   0x6474e551   /* Stack segment. */

/* Flags for p_flags.  See [ELF3] 2-3 and 2-4. */
#define PF_X 1          /* Executable. */
#define PF_W 2          /* Writable. */
#define PF_R 4          /* Readable. */

static bool setup_stack (void **esp);
static void pushw_stack (void **esp, void *word);	/* My Implementation */
static bool validate_segment (const struct Elf32_Phdr *, struct file *);
static bool load_segment (struct file *file, off_t ofs, uint8_t *upage,
                          uint32_t read_bytes, uint32_t zero_bytes,
                          bool writable);

/* Loads an ELF executable from FILE_NAME into the current thread.
   Stores the executable's entry point into *EIP
   and its initial stack pointer into *ESP.
   Returns true if successful, false otherwise. */
bool
load (const char *cmdline, void (**eip) (void), void **esp)
{
  struct thread *t = thread_current ();
  struct Elf32_Ehdr ehdr;
  struct file *file = NULL;
  off_t file_ofs;
  bool success = false;
  int i;
  /* My Implementation */
  char *file_name;						// actual file name
  char *cmd_str = palloc_get_page(0);	// page for storing thread's file name

  // temporary variables for iterating cmdline.
  struct list addr_list;
  char *token, *save_ptr;
  int argc = 0;

  if (cmd_str == NULL)
  	goto done;
  strlcpy(cmd_str, cmdline, PGSIZE);

  file_name = token = strtok_r (cmd_str, " ", &save_ptr);
  strlcpy (t->name, file_name, 16);

  /* My Implementation */
  /* Allocate and activate page directory. */
  t->pagedir = pagedir_create ();
  if (t->pagedir == NULL)
    goto done;

  /* My Implementation */
#ifdef VM
  /* Initialize a supplemental page table */
  t->sp_table = spt_create();
  if (t->sp_table == NULL)
	goto done;

  t->curr_mid = 1;
  t->mmap_table = malloc (sizeof (struct hash));
  if (t->mmap_table == NULL)
	goto done;
  if (!hash_init(t->mmap_table, hash_mid, mid_less, NULL))
	{
	  free(t->mmap_table);
	  t->mmap_table = NULL;
	  goto done;
	}

#endif
  /* My Implementation */

  process_activate ();

  /* file descriptor initialization */
  t->curr_fd = 3;
  /* file descriptor table initialization */
  t->fd_table = malloc (sizeof (struct hash));
  if (t->fd_table == NULL)
	goto done;
  if (!hash_init(t->fd_table, hash_fd, fd_less, NULL))
	{
	  free(t->fd_table);
	  t->fd_table = NULL;
	  goto done;
	}

  /* Open executable file. */
  lock_acquire(&filesys_mutex);
  file = filesys_open (file_name);
  if (file == NULL)
    {
      printf ("load: %s: open failed\n", file_name);
      goto file_done;
    }

  /* Set to hold the file to the current thread,
   * and make the file to deny write */
  file_deny_write(file);
  t->exec_holder = file;

  /* Read and verify executable header. */
  if (file_read (file, &ehdr, sizeof ehdr) != sizeof ehdr
      || memcmp (ehdr.e_ident, "\177ELF\1\1\1", 7)
      || ehdr.e_type != 2
      || ehdr.e_machine != 3
      || ehdr.e_version != 1
      || ehdr.e_phentsize != sizeof (struct Elf32_Phdr)
      || ehdr.e_phnum > 1024)
    {
      printf ("load: %s: error loading executable\n", file_name);
      goto file_done;
    }
  lock_release(&filesys_mutex);			/* My Implementation */


  /* Read program headers. */
  file_ofs = ehdr.e_phoff;
  for (i = 0; i < ehdr.e_phnum; i++)
    {
      struct Elf32_Phdr phdr;

      lock_acquire(&filesys_mutex);			/* My Implementation */

      if (file_ofs < 0 || file_ofs > file_length (file))
        goto file_done;
      file_seek (file, file_ofs);

      if (file_read (file, &phdr, sizeof phdr) != sizeof phdr)
        goto file_done;

      lock_release(&filesys_mutex);			/* My Implementation */


      file_ofs += sizeof phdr;
      switch (phdr.p_type)
        {
        case PT_NULL:
        case PT_NOTE:
        case PT_PHDR:
        case PT_STACK:
        default:
          /* Ignore this segment. */
          break;
        case PT_DYNAMIC:
        case PT_INTERP:
        case PT_SHLIB:
          goto done;
        case PT_LOAD:
          if (validate_segment (&phdr, file))
            {
              bool writable = (phdr.p_flags & PF_W) != 0;
              uint32_t file_page = phdr.p_offset & ~PGMASK;
              uint32_t mem_page = phdr.p_vaddr & ~PGMASK;
              uint32_t page_offset = phdr.p_vaddr & PGMASK;
              uint32_t read_bytes, zero_bytes;
              if (phdr.p_filesz > 0)
                {
                  /* Normal segment.
                     Read initial part from disk and zero the rest. */
                  read_bytes = page_offset + phdr.p_filesz;
                  zero_bytes = (ROUND_UP (page_offset + phdr.p_memsz, PGSIZE)
                                - read_bytes);
                }
              else
                {
                  /* Entirely zero.
                     Don't read anything from disk. */
                  read_bytes = 0;
                  zero_bytes = ROUND_UP (page_offset + phdr.p_memsz, PGSIZE);
                }
              if (!load_segment (file, file_page, (void *) mem_page,
                                 read_bytes, zero_bytes, writable))
                goto done;
            }
          else
            goto done;
          break;
        }
    }

  /* Set up stack. */
  if (!setup_stack (esp))
    goto done;

  /* My Implementation */
  /* Argument passing */
  list_init(&addr_list);
  for (; token != NULL; token = strtok_r (NULL, " ", &save_ptr))
  {
	// sizeof(addr_entry) = 12
	struct addr_entry *entry = (struct addr_entry *) malloc(12);
	if (entry == NULL)
	  goto clean;

	size_t copy_len = strnlen(token, ARG_LIMIT)+1;

	*esp -= copy_len;
	entry->addr = *esp;
	strlcpy(*esp, token, copy_len);
	list_push_front(&addr_list, &entry->elem);
	argc++;
  }

  *esp = (void *)((int)*esp & 0xfffffffc);  	// word-align

  pushw_stack(esp, NULL);

  while (!list_empty(&addr_list))
  {
	struct addr_entry *head = list_entry(list_pop_front(&addr_list),
										 struct addr_entry, elem);
	pushw_stack(esp, &head->addr);
	free(head);
  }
  pushw_stack(esp, esp); 	// argv pushing
  pushw_stack(esp, &argc); 	// argc pushing
  pushw_stack(esp, NULL); 	// (fake) return address

  palloc_free_page(cmd_str);	// free the temporary page
  /* My Implementation */

  /* Start address. */
  *eip = (void (*) (void)) ehdr.e_entry;
  success = true;


 clean:
   while (!list_empty(&addr_list))
   {
	 struct addr_entry *head = list_entry(list_pop_front(&addr_list),
										  struct addr_entry, elem);
	 free(head);
   }
   goto done;

 file_done:
   lock_release (&filesys_mutex);

 done:
   /* We arrive here whether the load is successful or not. */
   if (!success && file)
	 {
	   lock_acquire(&filesys_mutex);
	   file_close(file);
	   lock_release(&filesys_mutex);
	 }
   return success;
}

/* load() helpers. */

// static bool install_page (void *upage, void *kpage, bool writable);

/* Checks whether PHDR describes a valid, loadable segment in
   FILE and returns true if so, false otherwise. */
static bool
validate_segment (const struct Elf32_Phdr *phdr, struct file *file)
{
  /* p_offset and p_vaddr must have the same page offset. */
  if ((phdr->p_offset & PGMASK) != (phdr->p_vaddr & PGMASK))
    return false;

  /* p_offset must point within FILE. */
  lock_acquire(&filesys_mutex);
  if (phdr->p_offset > (Elf32_Off) file_length (file))
	{
	  lock_release(&filesys_mutex);
	  return false;
	}
  lock_release(&filesys_mutex);


  /* p_memsz must be at least as big as p_filesz. */
  if (phdr->p_memsz < phdr->p_filesz)
    return false;

  /* The segment must not be empty. */
  if (phdr->p_memsz == 0)
    return false;

  /* The virtual memory region must both start and end within the
     user address space range. */
  if (!is_user_vaddr ((void *) phdr->p_vaddr))
    return false;
  if (!is_user_vaddr ((void *) (phdr->p_vaddr + phdr->p_memsz)))
    return false;

  /* The region cannot "wrap around" across the kernel virtual
     address space. */
  if (phdr->p_vaddr + phdr->p_memsz < phdr->p_vaddr)
    return false;

  /* Disallow mapping page 0.
     Not only is it a bad idea to map page 0, but if we allowed
     it then user code that passed a null pointer to system calls
     could quite likely panic the kernel by way of null pointer
     assertions in memcpy(), etc. */
  if (phdr->p_vaddr < PGSIZE)
    return false;

  /* It's okay. */
  return true;
}

/* Loads a segment starting at offset OFS in FILE at address
   UPAGE.  In total, READ_BYTES + ZERO_BYTES bytes of virtual
   memory are initialized, as follows:

        - READ_BYTES bytes at UPAGE must be read from FILE
          starting at offset OFS.

        - ZERO_BYTES bytes at UPAGE + READ_BYTES must be zeroed.

   The pages initialized by this function must be writable by the
   user process if WRITABLE is true, read-only otherwise.

   Return true if successful, false if a memory allocation error
   or disk read error occurs. */
static bool
load_segment (struct file *file, off_t ofs, uint8_t *upage,
              uint32_t read_bytes, uint32_t zero_bytes, bool writable)
{
  ASSERT ((read_bytes + zero_bytes) % PGSIZE == 0);
  ASSERT (pg_ofs (upage) == 0);
  ASSERT (ofs % PGSIZE == 0);

  file_seek (file, ofs);
  while (read_bytes > 0 || zero_bytes > 0)
    {
      /* Do calculate how to fill this page.
         We will read PAGE_READ_BYTES bytes from FILE
         and zero the final PAGE_ZERO_BYTES bytes. */
      size_t page_read_bytes = read_bytes < PGSIZE ? read_bytes : PGSIZE;
      size_t page_zero_bytes = PGSIZE - page_read_bytes;

      /* My Implementation */

#ifdef VM
      struct s_page_table *spt;
	  if ((spt = thread_current()->sp_table) == NULL)
		return false;

	  // Register the spte to the table
	  if (!spte_reg_file (spt, upage, file, ofs, page_read_bytes, writable, false))
		  return false;

	  // renewal ofs
	  ofs += page_read_bytes;
	  /* My Implementation */
#else
      /* Get a page of memory. */
      uint8_t *kpage = palloc_get_page (PAL_USER);

      if (kpage == NULL)
        return false;

      /* Load this page. */
      lock_acquire(&filesys_mutex);
      if (file_read (file, kpage, page_read_bytes) != (int) page_read_bytes)
        {
    	  palloc_free_page(kpage);
    	  lock_release(&filesys_mutex);
          return false;
        }
      lock_release(&filesys_mutex);
      memset (kpage + page_read_bytes, 0, page_zero_bytes);

      /* Add the page to the process's address space. */
      if (!install_page (upage, kpage, writable))
        {
    	  palloc_free_page(kpage);
          return false;
        }
#endif
      /* Advance. */
      read_bytes -= page_read_bytes;
      zero_bytes -= page_zero_bytes;
      upage += PGSIZE;
    }

  return true;
}

/* Create a minimal stack by mapping a zeroed page at the top of
   user virtual memory. */
static bool
setup_stack (void **esp)
{
  uint8_t *kpage;
  bool success = false;

  /* My Implementation */
#ifdef VM
  struct fte *fte;

  lock_acquire(&frame_lock);

  fte = user_falloc_get (PAL_USER | PAL_ZERO, ((uint8_t *) PHYS_BASE) - PGSIZE);
  if (fte != NULL)
    {
	  kpage = fte->kpage;
      success = install_page (((uint8_t *) PHYS_BASE) - PGSIZE, kpage, true);

      // It uses proper logic optimization
      if (success
    	  && spte_reg_frame(thread_current()->sp_table, fte, true))
    		  // Register spte as a on-frame
    	  *esp = PHYS_BASE;
      else
    	{
    	  success = false;
    	  pagedir_clear_page(thread_current()->pagedir,
							 ((uint8_t *) PHYS_BASE) - PGSIZE);
    	  user_frame_free (fte);
    	}
    }

  lock_release(&frame_lock);

  /* My Implementation */
#else
  kpage = palloc_get_page (PAL_USER | PAL_ZERO);
  if (kpage != NULL)
    {
      success = install_page (((uint8_t *) PHYS_BASE) - PGSIZE, kpage, true);
      if (success)
        *esp = PHYS_BASE;
      else
    	palloc_free_page(kpage);
    }
#endif


  return success;
}

/* My Implementation */
/* Operation that pushes a word to the stack, specified by esp.
 * if word is NULL, then it ignores copying procedure. */
static void
pushw_stack (void **esp, void *word)
{
  if (word!=NULL)
	memcpy(*esp-4, word, 4);
  *esp -= 4;
}
/* My Implementation */

/* Adds a mapping from user virtual address UPAGE to kernel
   virtual address KPAGE to the page table.
   If WRITABLE is true, the user process may modify the page;
   otherwise, it is read-only.
   UPAGE must not already be mapped.
   KPAGE should probably be a page obtained from the user pool
   with palloc_get_page().
   Returns true on success, false if UPAGE is already mapped or
   if memory allocation fails. */
bool
install_page (void *upage, void *kpage, bool writable)
{
  struct thread *t = thread_current ();

  /* Verify that there's not already a page at that virtual
     address, then map our page there. */
  return (pagedir_get_page (t->pagedir, upage) == NULL
          && pagedir_set_page (t->pagedir, upage, kpage, writable));
}


/* My Implementation */
/* hash function for fd table. it immediately returns the fd of given fd entry.
 * fd itself will be a good hash value.  */
unsigned
hash_fd (const struct hash_elem *element, void *aux UNUSED)
{
  const struct fd_entry *fde = hash_entry (element, struct fd_entry, hash_elem);
  return fde->fd;
}

/* hash less function for fd table. it compares fd's of two elements. */
bool
fd_less (const struct hash_elem *a, const struct hash_elem *b, void *aux UNUSED)
{
  const struct fd_entry *fde_a = hash_entry (a, struct fd_entry, hash_elem);
  const struct fd_entry *fde_b = hash_entry (b, struct fd_entry, hash_elem);

  return fde_a->fd < fde_b->fd;
}

void delete_fde (struct hash_elem *element, void *aux UNUSED)
{
  struct fd_entry *fde;
  fde = hash_entry (element, struct fd_entry, hash_elem);
  file_close(fde->file);
  free(fde);
}

#ifdef VM
unsigned
hash_mid (const struct hash_elem *element, void *aux UNUSED)
{
  const struct mmap_entry *me = hash_entry (element, struct mmap_entry, hash_elem);
  return me->map_id;
}

/* hash less function for fd table. it compares fd's of two elements. */
bool
mid_less (const struct hash_elem *a, const struct hash_elem *b, void *aux UNUSED)
{
  const struct mmap_entry *me_a = hash_entry (a, struct mmap_entry, hash_elem);
  const struct mmap_entry *me_b = hash_entry (b, struct mmap_entry, hash_elem);

  return me_a->map_id < me_b->map_id;
}

void delete_me (struct hash_elem *element, void *aux UNUSED)
{
  struct mmap_entry *me;
  me = hash_entry (element, struct mmap_entry, hash_elem);
  if (!me->unmapped)
	{
	  map_write_back(thread_current()->sp_table, me);
	  lock_acquire(&filesys_mutex);
	  file_close(me->file);
	  lock_release(&filesys_mutex);
	}
  free(me);
}
#endif

/* It finds corresponding fd_entry of the given fd
 * from the current thread's fd_table.
 * If no such entry exists, it returns NULL. */
struct fd_entry *
fd_lookup (const int fd)
{
  struct fd_entry fde;
  struct hash_elem *elem;

  fde.fd = fd;
  /* It guarantees that this hash has no race condition,
   * since it is accessed by only one thread. */
  elem = hash_find (thread_current()->fd_table, &fde.hash_elem);
  return elem != NULL ? hash_entry (elem, struct fd_entry, hash_elem) : NULL;
}

#ifdef VM
struct mmap_entry *
mmap_lookup (const int mid)
{
  struct mmap_entry me;
  struct hash_elem *elem;

  me.map_id = mid;
  /* It guarantees that this hash has no race condition,
   * since it is accessed by only one thread. */
  elem = hash_find (thread_current()->mmap_table, &me.hash_elem);
  return elem != NULL ? hash_entry (elem, struct mmap_entry, hash_elem) : NULL;
}
#endif

/* My Implementation */
