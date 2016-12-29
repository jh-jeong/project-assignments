/*
 * frame.c
 *
 *  Created on: 2015. 5. 1.
 *      Author: biscuit
 */

#include "vm/frame.h"
#include "vm/page.h"
#include "vm/swap.h"
#include "threads/thread.h"
#include "threads/vaddr.h"
#include "threads/malloc.h"
#include "userprog/pagedir.h"
#include "userprog/process.h"
#include "filesys/file.h"
#include <stddef.h>

#define LOOP_MAX 1024	/* Looping limit when the finding for evict occurs */

static struct fte *evict_frame (void);

static struct list_elem *ft_cursor;

void
frame_init(void)
{
  list_init(&frame_table);
  lock_init(&frame_lock);
}

struct fte*
user_falloc_get (enum palloc_flags flag, void *upage)
{
  ASSERT (pg_ofs (upage) == 0);
  void *kpage;
  struct thread *t;
  struct fte *fte;
  if ((flag & PAL_USER) == 0)
	return NULL;

  fte = malloc(sizeof (struct fte));
  if (fte == NULL)
	return NULL;

  while ((kpage = palloc_get_page(flag)) == NULL)
	{
	  struct fte *victim;
	  struct spte *spte;

	  if ((victim = evict_frame()) == NULL)
		PANIC ("all frames are busy.");

	  t = victim->owner;
	  if ((spte = spte_lookup(t->sp_table, victim->upage)) == NULL)
		{
		  free(fte);
		  return NULL;
		}

	  void *frame = victim->kpage;
	  bool dirty = pagedir_is_dirty (t->pagedir, victim->upage);

	  lock_acquire (&t->sp_table->lock);

	  spte->dirty = dirty;
	  if (!dirty)
		  spte->status = (spte->file != NULL) ? IN_FILE : ALL_ZERO;
	  else if (spte->mmap)
		{
		  ASSERT (spte->file != NULL);
		  lock_acquire(&filesys_mutex);
		  file_write_at(spte->file, victim->kpage, spte->read_bytes, spte->f_offset);
		  lock_release(&filesys_mutex);
		  spte->status = IN_FILE;
		}
	  else
		{
		  spte->swap_index = swap_out(frame);
		  spte->status = IN_SWAP;
		}
	  spte->fte = NULL;
	  pagedir_clear_page (t->pagedir, victim->upage);
	  user_frame_free(victim);

	  lock_release (&t->sp_table->lock);
  	}

  fte->upage = upage;
  fte->kpage = kpage;
  fte->owner = thread_current();
  fte->pin = 0;

  list_push_back(&frame_table, &fte->elem);

  return fte;
}

void
user_frame_free (struct fte *target)
{
  ASSERT (target != NULL);
  ASSERT (target->kpage >= PHYS_BASE);

  ASSERT (!list_empty(&frame_table));
  if (ft_cursor == &target->elem)
  	ft_cursor = list_next(ft_cursor);
  list_remove(&target->elem);
  palloc_free_page(target->kpage);
  free(target);
}

void
clean_frame (struct thread *t)
{
  struct list_elem *e;

  lock_acquire(&frame_lock);

  ASSERT (!list_empty(&frame_table));
  for (e = list_begin(&frame_table); e != list_end(&frame_table);)
	{
	  struct fte* f = list_entry (e, struct fte, elem);
	  struct list_elem *v = list_next(e);
	  if (f->owner == t)
		{
		  if (ft_cursor == e)
			ft_cursor = list_next(ft_cursor);
		  pagedir_clear_page(thread_current()->pagedir, f->upage);
		  user_frame_free(f);
		}
	  e = v;
	}
  lock_release(&frame_lock);
}

static struct fte *
evict_frame (void)
{
  struct fte *candidate = NULL;
  struct thread *t = thread_current();
  int loop_count = 0;

  ASSERT (!list_empty(&frame_table));
  while (true)
	{
	  if ( ++loop_count > LOOP_MAX)
		return NULL;
	  if (ft_cursor == NULL || ft_cursor == list_end(&frame_table))
	  	ft_cursor = list_begin(&frame_table);
	  candidate = list_entry (ft_cursor, struct fte, elem);
	  ft_cursor = list_next(ft_cursor);
	  if (candidate->pin)
		continue;
	  if (!pagedir_is_accessed(t->pagedir, candidate->upage))
		break;
	  pagedir_set_accessed(t->pagedir, candidate->upage, false);
	}

  return candidate;
}
