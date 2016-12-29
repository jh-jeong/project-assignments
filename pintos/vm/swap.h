/*
 * swap.h
 *
 *  Created on: 2015. 5. 4.
 *      Author: biscuit & kying
 */
#ifndef SWAP_H
#define SWAP_H

#include "devices/disk.h"
#include "threads/vaddr.h"
#include <bitmap.h>
#include <stddef.h>

/* Number of sectors that a page contains */
#define SECTORS_PER_PAGE (PGSIZE / DISK_SECTOR_SIZE)

/* Swap table enviorment */
struct disk *swap;
struct bitmap *swap_table;

/* Mutex lock for swap table */
struct lock swap_mutex;

void swap_init(void);
size_t swap_out (void *);
void swap_in (void *, size_t);
void swap_free (size_t);

#endif
