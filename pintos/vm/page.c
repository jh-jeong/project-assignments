/*
 * page.c
 *
 *  Created on: 2015. 5. 2.
 *      Author: biscuit
 */

#include "vm/page.h"
#include "vm/frame.h"
#include "vm/swap.h"
#include "threads/malloc.h"
#include "threads/vaddr.h"
#include "userprog/process.h"
#include "userprog/pagedir.h"
#include "filesys/file.h"
#include <debug.h>
#include <stddef.h>
#include <string.h>

static hash_hash_func spt_hash;
static hash_less_func spt_less;
static hash_action_func spte_free;

struct s_page_table *
spt_create (void)
{
  struct s_page_table *spt = malloc(sizeof (struct s_page_table));
  if (spt == NULL)
	return NULL;
  if(!hash_init(&spt->table, spt_hash, spt_less, NULL))
	{
	  free(spt);
	  return NULL;
	}
  lock_init(&spt->lock);
  return spt;
}

void
spt_destroy (struct s_page_table *spt)
{
  if (spt == NULL)
	return;
  hash_destroy (&spt->table, spte_free);
  free(spt);
}

bool
spte_reg_frame (struct s_page_table *spt, struct fte *fte, bool writable)
{
  ASSERT (is_user_vaddr (fte->upage));
  ASSERT (pg_ofs (fte->upage) == 0);
  ASSERT (spt != NULL);

  struct spte *spte = malloc(sizeof (struct spte));
  if (spte == NULL)
	return false;

  spte->file = NULL;
  spte->page = fte->upage;
  spte->status = ON_FRAME;
  spte->writable = writable;
  spte->dirty = false;
  spte->fte = fte;
  spte->mmap = false;

  bool success = true;

  lock_acquire (&spt->lock);
  if (hash_insert(&spt->table, &spte->elem))
	{
	  free(spte);
	  success = false;
	}
  lock_release (&spt->lock);

  return success;
}

bool
spte_reg_zero (struct s_page_table *spt, void *upage, bool writable)
{
  ASSERT (is_user_vaddr (upage));
  ASSERT (pg_ofs (upage) == 0);
  ASSERT (spt != NULL);

  struct spte *spte = malloc(sizeof (struct spte));
  if (spte == NULL)
	return false;

  spte->file = NULL;
  spte->page = upage;
  spte->status = ALL_ZERO;
  spte->writable = writable;
  spte->read_bytes = 0;
  spte->zero_bytes = PGSIZE;
  spte->dirty = false;
  spte->fte = NULL;
  spte->mmap = false;

  bool success = true;

  lock_acquire (&spt->lock);
  if (hash_insert(&spt->table, &spte->elem))
	{
	  free(spte);
	  success = false;
	}
  lock_release (&spt->lock);

  return success;
}

bool
spte_reg_file (struct s_page_table *spt, void *upage, struct file *file,
			   off_t offset, uint32_t page_read_bytes, bool writable, bool mmap)
{
  ASSERT (is_user_vaddr (upage));
  ASSERT (pg_ofs (upage) == 0);
  ASSERT (spt != NULL);

  struct spte *spte = malloc(sizeof (struct spte));
  if (spte == NULL)
	return false;

  spte->page = upage;
  spte->file = file;
  spte->f_offset = offset;
  spte->read_bytes = page_read_bytes;
  spte->zero_bytes = PGSIZE - page_read_bytes;
  spte->writable = writable;
  spte->status = (page_read_bytes == 0) ? ALL_ZERO : IN_FILE;
  spte->dirty = false;
  spte->fte = NULL;
  spte->mmap = mmap;

  bool success = true;

  // Register the spte to the table
  lock_acquire(&spt->lock);
  if (hash_insert(&spt->table, &spte->elem))
	{
	  free(spte);
	  success = false;
	}
  lock_release(&spt->lock);

  return success;
}

void
map_write_back (struct s_page_table *spt, struct mmap_entry *me)
{
  ASSERT (spt != NULL);
  ASSERT (me != NULL);

  struct file *file = me->file;
  struct spte *spte;
  struct thread *t = thread_current();
  off_t size = me->size;
  off_t ofs = 0;
  void *temp;
  void *sys_page = palloc_get_page(0);

  lock_acquire(&frame_lock);
  for (temp = me->start; temp < me->end; temp += PGSIZE)
	{
	  spte = spte_lookup(spt, temp);

	  if (pagedir_is_dirty(t->pagedir, spte->page))
		{
		  memcpy(sys_page, temp, PGSIZE);
		  lock_acquire(&filesys_mutex);
		  file_write_at(file, sys_page, (size < PGSIZE) ? size : PGSIZE, ofs);
		  lock_release(&filesys_mutex);
		}

	  if (spte->status == ON_FRAME)
		user_frame_free(spte->fte);
	  hash_delete(&t->sp_table->table, &spte->elem);
	  free(spte);
	  pagedir_clear_page(t->pagedir, temp);

	  ofs += PGSIZE;
	  size -= PGSIZE;
	}
  lock_release(&frame_lock);

  palloc_free_page(sys_page);

}

struct spte *
spte_lookup (struct s_page_table *spt, const void *uaddr)
{
  ASSERT (spt != NULL);

  void *upage = pg_round_down(uaddr);
  struct spte temp;
  struct hash_elem *h;

  temp.page = upage;
  lock_acquire (&spt->lock);
  h = hash_find (&spt->table, &temp.elem);
  lock_release (&spt->lock);

  return (h == NULL) ? NULL : hash_entry(h, struct spte, elem);
}

bool spte_fetch_data (struct spte *spte, void *kpage)
{
  ASSERT (pg_ofs (kpage) == 0);
  ASSERT (spte != NULL);

  bool re_acq = false;

  switch (spte->status)
  {
  case IN_FILE:
	if (!lock_held_by_current_thread (&filesys_mutex))
	  lock_acquire(&filesys_mutex);
	else re_acq = true;
	file_seek (spte->file, spte->f_offset);
	off_t read = file_read (spte->file, kpage, spte->read_bytes);
	if (!re_acq)
	  lock_release(&filesys_mutex);
	if (read != spte->read_bytes)
	  return false;
  case ALL_ZERO:
	memset (kpage + spte->read_bytes, 0, spte->zero_bytes);
	break;
  case IN_SWAP:
	swap_in (kpage, spte->swap_index);
	break;
  default:
	break;
  }

  return true;
}

static void
spte_free (struct hash_elem *e, void *aux UNUSED)
{
  struct spte* spte = hash_entry(e, struct spte, elem);
  if (spte->status == IN_SWAP)
	swap_free (spte->swap_index);
  free(spte);
}

static unsigned
spt_hash (const struct hash_elem *e, void *aux UNUSED)
{
  void *page = hash_entry(e, struct spte, elem)->page;
  return hash_int ( (int) page );
}

static bool
spt_less (const struct hash_elem *a, const struct hash_elem *b, void *aux UNUSED)
{
  void *page_a = hash_entry(a, struct spte, elem)->page;
  void *page_b = hash_entry(b, struct spte, elem)->page;
  return page_a < page_b;
}
