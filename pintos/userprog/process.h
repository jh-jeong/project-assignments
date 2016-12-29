#ifndef USERPROG_PROCESS_H
#define USERPROG_PROCESS_H

#include "threads/thread.h"
#include "threads/synch.h"
#include "threads/vaddr.h"
#include "filesys/off_t.h"

// Limit on the length of the arguments
#define ARG_LIMIT 127		/* My Implementation */

// Maximum stack size ; it's 8MB(8192KB).
#define STACK_SIZE 8388608

tid_t process_execute (const char *file_name);
int process_wait (tid_t);
void process_exit (void);
void process_activate (void);

/* My Implementation */
/* hash functions for file descriptor table. */
hash_hash_func hash_fd;
hash_less_func fd_less;

hash_action_func delete_fde;

hash_hash_func hash_mid;
hash_less_func mid_less;

hash_action_func delete_me;

struct fd_entry *fd_lookup (const int fd);
struct mmap_entry *mmap_lookup (const int mid);

/* load() helpers. */
bool install_page (void *upage, void *kpage, bool writable);

/* file descriptor entry, which is stored to fd table by a hash_elem.
 * it maps fd to its file structure. */
struct fd_entry
  {
  struct hash_elem hash_elem;
  int fd;
  struct file* file;
  };

/* Used to store the address of a string to a list.
 * With the address, it also contains a list_elem. */
struct addr_entry
  {
  char **addr;
  struct list_elem elem;
  };

extern struct lock exec_mutex;
extern struct semaphore exec_wait_load;

extern struct lock filesys_mutex;

/* My Implementation */

#endif /* userprog/process.h */
