/*
 * swap.c
 *
 *  Created on: 2015. 5. 4.
 *      Author: biscuit & kying
 */
#include "vm/swap.h"
#include "threads/synch.h"
#include <debug.h>
#include <stdbool.h>

static size_t cur_index = 0;
static bool reset_flag = false;

void
swap_init(void)
{
  ASSERT (!(PGSIZE % DISK_SECTOR_SIZE));

  swap = disk_get(1, 1);
  ASSERT (swap);

  swap_table = bitmap_create( disk_size(swap) / SECTORS_PER_PAGE );
  ASSERT (swap_table);

  lock_init(&swap_mutex);
}

/* It swaps out the given page to the swap disk. */
size_t
swap_out (void *kpage)
{
  ASSERT (pg_ofs (kpage) == 0);
  disk_sector_t sector;

  lock_acquire(&swap_mutex);
  // This loop runs over at most twice.
  while ((cur_index = bitmap_scan_and_flip (swap_table, cur_index, 1, false)) == BITMAP_ERROR)
	{
	  if (reset_flag)
		PANIC ("swap disk has no more space to write");
	  cur_index = 0;
	  reset_flag = true;
	}
  reset_flag = false;

  for (sector = cur_index * SECTORS_PER_PAGE;
	   sector < cur_index * SECTORS_PER_PAGE + SECTORS_PER_PAGE;
	   sector++)
	{
	  disk_write(swap, sector, kpage);
	  kpage += DISK_SECTOR_SIZE;
	}
  lock_release(&swap_mutex);

  return cur_index;
}

void
swap_free (size_t index)
{
  lock_acquire(&swap_mutex);
  ASSERT (index < bitmap_size(swap_table));
  ASSERT (bitmap_test (swap_table, index) == true);
  bitmap_reset (swap_table, index);
  lock_release(&swap_mutex);
}

void
swap_in (void *kpage, size_t index)
{
  ASSERT (pg_ofs (kpage) == 0);
  disk_sector_t sector;

  lock_acquire(&swap_mutex);
  ASSERT (index < bitmap_size(swap_table));
  ASSERT (bitmap_test (swap_table, index) == true);

  for (sector = index * SECTORS_PER_PAGE;
	   sector < index * SECTORS_PER_PAGE + SECTORS_PER_PAGE;
	   sector++)
	{
	  disk_read(swap, sector, kpage);
	  kpage += DISK_SECTOR_SIZE;
	}
  bitmap_reset (swap_table, index);
  lock_release(&swap_mutex);
}


