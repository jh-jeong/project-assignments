/*
 * frame.h
 *
 *  Created on: 2015. 5. 1.
 *      Author: biscuit
 */
#ifndef FRAME_H
#define FRAME_H

#include "threads/synch.h"
#include "threads/palloc.h"
#include <list.h>
#include <stdint.h>
#include <debug.h>
#include <stdbool.h>

/* An entry for the frame table */
struct fte
{
  void *upage;				// user page
  void *kpage;				// kernel page
  struct thread *owner;		// thread which currently own this frame
  struct list_elem elem;	// list element
  uint32_t pin;				// pin checking
};

/* Frame table enviornment */
struct list frame_table;	// frame abstraction
struct lock frame_lock;		// lock for frame_table;

void frame_init(void);

struct fte *user_falloc_get (enum palloc_flags, void*);
void user_frame_free (struct fte *);
void clean_frame (struct thread *);

#endif
