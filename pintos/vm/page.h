/*
 * page.h
 *
 *  Created on: 2015. 5. 2.
 *      Author: biscuit
 */
#ifndef PAGE_H
#define PAGE_H

#include "filesys/off_t.h"
#include "userprog/syscall.h"
#include <hash.h>
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* It indicates four states that an spte can happen */
enum page_state { ON_FRAME, IN_FILE, IN_SWAP, ALL_ZERO };

/* Supplymental page table enviornment */
struct s_page_table
{
  struct hash table;
  struct lock lock;
};

/* structure for supplymental page table element */
struct spte
{
  void *page;
  enum page_state status;
  bool writable;
  bool dirty;
  struct hash_elem elem;

  // IN_FILE
  struct file *file;
  off_t f_offset;
  int32_t read_bytes;
  int32_t zero_bytes;

  // IN_SWAP
  /* page number in swap disk,
   * set only when it is IN_SWAP */
  size_t swap_index;

  // ON_FRAME
  struct fte* fte;

  bool mmap;

};

struct s_page_table *spt_create (void);
void spt_destroy (struct s_page_table *);
bool spte_reg_frame (struct s_page_table *, struct fte *, bool);
bool spte_reg_zero (struct s_page_table *, void *, bool);
bool spte_reg_file (struct s_page_table *, void *, struct file *, off_t , uint32_t , bool, bool);
struct spte *spte_lookup (struct s_page_table *, const void *);
bool spte_fetch_data (struct spte *, void *);
void map_write_back (struct s_page_table *, struct mmap_entry *);

#endif
