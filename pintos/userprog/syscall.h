#ifndef USERPROG_SYSCALL_H
#define USERPROG_SYSCALL_H

#include "threads/thread.h"
#include "threads/interrupt.h"
#include "filesys/off_t.h"

#define SYSCALL_MAX 32		// Maximum enum length for system calls

#define STDERR_FILENO 2   	// reserved

void syscall_init (void);

/* My Implementation */
int handler_halt 		(struct intr_frame *);
int handler_exit 		(int, struct intr_frame *);
int handler_exec 		(const char *, struct intr_frame *);
int handler_wait 		(tid_t, struct intr_frame *);
int handler_create 		(const char *, unsigned, struct intr_frame *);
int handler_remove 		(const char *, struct intr_frame *);
int handler_open 		(const char *, struct intr_frame *);
int handler_filesize 	(int, struct intr_frame *);
int handler_read 		(int, void *, unsigned, struct intr_frame *);
int handler_write 		(int, const void *, unsigned, struct intr_frame *);
int handler_seek 		(int, unsigned, struct intr_frame *);
int handler_tell 		(int, struct intr_frame *);
int handler_close 		(int, struct intr_frame *);
#ifdef VM
int handler_mmap 		(int, void *, struct intr_frame *);
int handler_munmap 		(int, struct intr_frame *);
#endif

// struct which contains informations about system call handlers
struct handler_info
{
  void *handler;
  int arg_num;
};

/* An entry for mmap table */
struct mmap_entry
  {
  struct hash_elem hash_elem;
  int map_id;
  struct file *file;	// file that is connected that mid
  void *start, *end;	// page that start to mmap, end to, resp.
  off_t size;			// actual size of mmap
  bool unmapped;		// for checking that the entry is unmapped
  };
/* My Implementation */

#endif /* userprog/syscall.h */
