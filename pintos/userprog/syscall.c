#include "userprog/syscall.h"
#include "userprog/process.h"
#include "userprog/pagedir.h"
#include <stdio.h>
#include <syscall-nr.h>
#include <string.h>
#include "threads/malloc.h"
#include "threads/interrupt.h"
#include "threads/thread.h"
#include "threads/vaddr.h"
#include "threads/init.h"
#include "devices/input.h"
#ifdef FILESYS
#include "filesys/filesys.h"
#include "filesys/file.h"
#endif
#ifdef VM
#include "vm/page.h"
#include "vm/frame.h"
#endif

static void syscall_handler (struct intr_frame *);

/* My Implementation */

// Check whether the given address is a valid user virtual address.
static bool is_valid_uaddr (const void *uaddr, void *esp);

#ifdef VM
static void try_pin (const void *);
static void try_unpin (const void *);
#endif

// void-parameter general handler
typedef int (*handler0) (struct intr_frame *);
// one-parameter general handler
typedef int (*handler1) (size_t, struct intr_frame *);
// two-parameter general handler
typedef int (*handler2) (size_t, size_t, struct intr_frame *);
// three-parameter general handler
typedef int (*handler3) (size_t, size_t, size_t, struct intr_frame *);

static void exit_invalid_vaddr (const void *vaddr, struct intr_frame *f);

static struct handler_info sys_vec[SYSCALL_MAX] =
  {
	  { handler_halt, 0 },		// SYS_HALT
	  { handler_exit, 1 },		// SYS_EXIT
	  { handler_exec, 1 },		// SYS_EXEC
	  { handler_wait, 1 }, 		// SYS_WAIT
	  { handler_create, 2 },	// SYS_CREATE
	  { handler_remove, 1 }, 	// SYS_REMOVE
	  { handler_open, 1 }, 		// SYS_OPEN
	  { handler_filesize, 1 },	// SYS_FILESIZE
	  { handler_read, 3 },		// SYS_READ
	  { handler_write, 3 }, 	// SYS_WRITE
	  { handler_seek, 2 },		// SYS_SEEK
	  { handler_tell, 1 }, 		// SYS_TELL
	  { handler_close, 1 },		// SYS_CLOSE
#ifdef VM
	  { handler_mmap, 2 },		// SYS_MMAP
	  { handler_munmap, 1 }		// SYS_MUNMAP
#endif
  };

/* My Implementation */


void
syscall_init (void) 
{
  intr_register_int (0x30, 3, INTR_ON, syscall_handler, "syscall");
  lock_init(&filesys_mutex);
}

static void
syscall_handler (struct intr_frame *f)
{
  /* My Implementation */
  struct handler_info *h_info;
  void *handler;
  int *esp = f->esp;
  int sys_num, ret_val = 0;

  exit_invalid_vaddr(esp, f);
#ifdef VM
  try_pin (esp);
  thread_current()->user_esp = esp;
#endif
  sys_num = *esp;
  if((h_info = sys_vec + sys_num) == NULL)
	goto base;		// Case of unimplemented system calls

  handler = h_info->handler;
  switch (h_info->arg_num)
  {
  case 0:
	ret_val = ((handler0) handler)(f);
	break;
  case 1:
	exit_invalid_vaddr(esp+1, f);
#ifdef VM
	try_pin (esp+1);
#endif
	ret_val = ((handler1) handler)(esp[1], f);
	break;
  case 2:
	exit_invalid_vaddr(esp+1, f);
	exit_invalid_vaddr(esp+2, f);
#ifdef VM
	try_pin (esp+1);
	try_pin (esp+2);
#endif
	ret_val = ((handler2) handler)(esp[1], esp[2], f);
	break;
  case 3:
  	exit_invalid_vaddr(esp+1, f);
	exit_invalid_vaddr(esp+2, f);
	exit_invalid_vaddr(esp+3, f);
#ifdef VM
	try_pin (esp+1);
	try_pin (esp+2);
	try_pin (esp+3);
#endif
  	ret_val = ((handler3) handler)(esp[1], esp[2], esp[3], f);
  	break;
  // Impossible case
  default: printf("Invalid system call argument number: [%d] %d", sys_num, h_info->arg_num);
  }

#ifdef VM
  int i = 0;
  for (; i <= h_info->arg_num; i++)
	try_unpin (esp+i);
#endif
  f->eax = ret_val;		// Setting EAX for system call return.
  return;

  /* My Implementation */
  NOT_REACHED ();
 base:
 /* Old Implementation */
  printf ("system call!\n");
  thread_exit ();
  /* Old Implementation */
}

/* My Implementation */

int
handler_halt (struct intr_frame *f UNUSED)
{
  power_off();
  return 0;
}

int
handler_exit (int status, struct intr_frame *f)
{
  struct tc_block *tcb;
  struct thread *curr = thread_current();
#ifdef VM
  int *esp = f->esp;
  // If the thread can reach to this,
  // then esp must be pinned, possibly esp+1 may not.
  try_unpin (esp);
  try_unpin (esp+1);
#endif

  tcb = tcb_lookup (curr->tid);
  tcb->exit_code = status;
  tcb->exit_flag = true;

  printf ("%s: exit(%d)\n", curr->name, status);
  thread_exit ();
  return 0;
}

int
handler_exec (const char *cmd_line, struct intr_frame *f)
{
  exit_invalid_vaddr(cmd_line, f);
#ifdef VM
  try_pin (cmd_line);
#endif
  tid_t tid = process_execute (cmd_line);
#ifdef VM
  try_unpin (cmd_line);
#endif
  return tid;
}

int
handler_wait (tid_t tid, struct intr_frame *f UNUSED)
{
  return process_wait(tid);
}

int
handler_create (const char *file, unsigned initial_size, struct intr_frame *f)
{
  bool success;
  exit_invalid_vaddr(file, f);
#ifdef VM
  try_pin (file);
#endif

  lock_acquire(&filesys_mutex);
  success = filesys_create (file, initial_size);
  lock_release(&filesys_mutex);
#ifdef VM
  try_unpin (file);
#endif
  return success;
}

int
handler_remove (const char *file, struct intr_frame *f)
{
  bool success;
  exit_invalid_vaddr(file, f);
#ifdef VM
  try_pin (file);
#endif

  lock_acquire(&filesys_mutex);
  success = filesys_remove (file);
  lock_release(&filesys_mutex);
#ifdef VM
  try_unpin (file);
#endif
  return success;
}

int
handler_open (const char *file, struct intr_frame *f)
{
  struct file *open_file;
  struct fd_entry *fde;
  struct thread *curr = thread_current();

  exit_invalid_vaddr(file, f);
#ifdef VM
  try_pin (file);
#endif

  fde = malloc(sizeof (struct fd_entry));

  lock_acquire(&filesys_mutex);
  open_file = filesys_open(file);
  lock_release(&filesys_mutex);

  if (open_file == NULL || fde == NULL)
  {
	free(fde);
	return -1;
  }

  fde->file = open_file;
  fde->fd = curr->curr_fd++;
  // Assert that each fd_table has no collision at any time.
  // fd_table does not have race condition, since it is accessed by only one thread.
  ASSERT (hash_replace(curr->fd_table, &fde->hash_elem) == NULL);

#ifdef VM
  try_unpin (file);
#endif

  return fde->fd;
}

int
handler_filesize (int fd, struct intr_frame *f UNUSED)
{
  struct fd_entry *fde;
  off_t size;
  if((fde = fd_lookup(fd)) == NULL)
	return -1;

  lock_acquire(&filesys_mutex);
  size = file_length(fde->file);
  lock_release(&filesys_mutex);

  return size;
}

int
handler_read (int fd, void *buffer, unsigned size, struct intr_frame *f)
{
  struct fd_entry *fde;
  off_t act_size;

  exit_invalid_vaddr(buffer, f);
#ifdef VM
  try_pin (buffer);

  struct spte *spte;
  if ((spte = spte_lookup (thread_current()->sp_table, buffer)) != NULL
	  && !spte->writable)
	handler_exit(-1, f);
#endif


  if (fd == STDIN_FILENO)
  {
	unsigned i = 0;
	char byte_read = 0;
	for( ; i < size && (byte_read = input_getc()) != 0x0a	// New-line
					&& byte_read != 0x0d					// Enter
					&& byte_read != 0x1a ; i++)				// EOF
	{
	  ((char *)buffer)[i] = byte_read;
	  printf("%c", byte_read);
	}
	printf("\n");
	return i;
  }
  if ((fde = fd_lookup(fd)) == NULL)	// It also includes the case when fd is STDOUT or STDERR
  	return -1;

  lock_acquire(&filesys_mutex);
  act_size = file_read(fde->file, buffer, size);
  lock_release(&filesys_mutex);
#ifdef VM
  try_unpin (buffer);
#endif
  return act_size;
}

int
handler_write (int fd, const void *buffer, unsigned size, struct intr_frame *f)
{
  struct fd_entry *fde;
  off_t act_size;

  exit_invalid_vaddr(buffer, f);
#ifdef VM
  try_pin (buffer);
#endif
  if (fd == STDOUT_FILENO)
  {
	putbuf(buffer, size);
	return size;
  }
  if ((fde = fd_lookup(fd)) == NULL)	// It also includes the case when fd is STDIN or STDERR
	return 0;

  lock_acquire(&filesys_mutex);
  act_size = file_write(fde->file, buffer, size);
  lock_release(&filesys_mutex);
#ifdef VM
  try_unpin (buffer);
#endif
  return act_size;
}

int
handler_seek (int fd, unsigned position, struct intr_frame *f UNUSED)
{
  struct fd_entry *fde;

  if((fde = fd_lookup(fd)) == NULL || ((int32_t) position) < 0)
  	return -1;
  file_seek(fde->file, position);	// No need to synchronize.
  return 0;
}

int
handler_tell (int fd, struct intr_frame *f UNUSED)
{
  struct fd_entry *fde;

  if((fde = fd_lookup(fd)) == NULL)
	handler_exit(-1, f);

  return file_tell(fde->file);		// No need to synchronize.
}

int
handler_close (int fd, struct intr_frame *f UNUSED)
{
  struct fd_entry *fde;

  if((fde = fd_lookup(fd)) == NULL)
  	return -1;

  lock_acquire(&filesys_mutex);
  file_close(fde->file);
  lock_release(&filesys_mutex);

  hash_delete(thread_current()->fd_table, &fde->hash_elem);
  free(fde);

  return 0;
}

#ifdef VM
int
handler_mmap (int fd, void *addr, struct intr_frame *f UNUSED)
{
  struct fd_entry *fde;
  struct file *file;
  struct thread* t = thread_current();
  struct mmap_entry *me;
  off_t size;
  void *temp;

  if (fd == STDIN_FILENO
	  || fd == STDOUT_FILENO
	  || addr == 0
	  || pg_ofs(addr) != 0
	  || (fde = fd_lookup(fd)) == NULL)
	return -1;

  lock_acquire(&filesys_mutex);
  size = file_length(file = file_reopen(fde->file));
  lock_release(&filesys_mutex);

  if (size == 0
	  || pg_round_up (addr + size) > PHYS_BASE - STACK_SIZE )
	return -1;

  ASSERT (file != NULL);
  ASSERT (t->sp_table != NULL);

  lock_acquire(&frame_lock);

  for (temp = addr; temp < pg_round_up (addr+size); temp += PGSIZE)
	if (spte_lookup(t->sp_table, temp) != NULL)
	  goto fail;

  off_t ofs = 0;
  for (temp = addr; temp < pg_round_up (addr+size); temp += PGSIZE)
	{
	  if (!spte_reg_file (t->sp_table, temp, file, ofs,
						  (size-ofs >= PGSIZE) ? PGSIZE : (size-ofs),
						  true, true))
		{
		  temp -= PGSIZE;
		  for (; temp >= addr; temp -= PGSIZE)
			{
			  struct spte *spte = spte_lookup(t->sp_table, temp);
			  hash_delete(&t->sp_table->table, &spte->elem);
			  free(spte);
			}
		  goto fail;
		}
	  ofs += PGSIZE;
	}

  lock_release(&frame_lock);

  me = malloc(sizeof (struct mmap_entry));
  if (me == NULL)
	return -1;

  me->map_id = t->curr_mid++;
  me->file = file;
  me->size = size;
  me->start = addr;
  me->end = pg_round_up (addr+size);
  me->unmapped = false;

  if (hash_insert(t->mmap_table, &me->hash_elem))
	{
	  free(me);
	  return -1;
	}

  return me->map_id;

 fail:
  lock_release(&frame_lock);
  return -1;
}

int
handler_munmap (int mapping, struct intr_frame *f UNUSED)
{
  struct mmap_entry *me;
  if ((me = mmap_lookup(mapping)) == NULL)
	{
	  printf ("[MUNMAP] there's no such map_id.\n");
	  return -1;
	}
  if (!me->unmapped)
	{
	  map_write_back(thread_current()->sp_table, me);
	  lock_acquire(&filesys_mutex);
	  file_close(me->file);
	  lock_release(&filesys_mutex);
	  me->unmapped = true;
	}
  return 0;
}
#endif


/* It checks wheater the given vaddr is valid,
 * and exit the thread if not so.
 * Also, if the address is valid, it pins the frame that used by the address */
static void
exit_invalid_vaddr (const void *vaddr, struct intr_frame *f)
{
  void *esp = f->esp;

  if (!is_valid_uaddr(vaddr, esp))
	handler_exit(-1, f);
}

/* It checks the given user virtual address's
 * - Non-nullity
 * - Whether the address is user address
 * - Whether the address is mapped */
static bool
is_valid_uaddr (const void *uaddr, void *esp)
{
#ifdef VM
  struct thread *t = thread_current();
  struct spte* spte;
  return (uaddr != NULL
		  && is_user_vaddr(uaddr)
		  && t->sp_table != NULL
		  && ((spte = spte_lookup (t->sp_table, uaddr)) != NULL
			  || (uaddr >= PHYS_BASE - STACK_SIZE && esp <= uaddr)));
			  // the case when the address accesses to the stack
#else
  return (uaddr != NULL && is_user_vaddr(uaddr)
		  && pagedir_get_page (thread_current()->pagedir, uaddr) != NULL);
#endif
}

#ifdef VM
static void
try_pin (const void *uaddr)
{
  struct spte* spte;
  lock_acquire(&frame_lock);
  if ((spte = spte_lookup (thread_current()->sp_table, uaddr)) != NULL
	  && spte->status == ON_FRAME)
	spte->fte->pin = true;
  lock_release (&frame_lock);
}

static void
try_unpin (const void *uaddr)
{
  struct s_page_table *spt = thread_current()->sp_table;
  struct spte *spte;

  lock_acquire (&frame_lock);
  if ((spte = spte_lookup(spt, uaddr)) != NULL
	  && spte->status == ON_FRAME)
	spte->fte->pin = false;
  lock_release (&frame_lock);
}
#endif
/* My implementation */
