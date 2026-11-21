// corpus: CON31-C noncompliant
#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <pthread.h>
#include <signal.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <wchar.h>

#include <stdatomic.h>
#include <stddef.h>
#include <threads.h>
 
mtx_t lock;
/* Atomic so multiple threads can modify safely */
atomic_int completed = 0;
enum { max_threads = 5 }; 

int do_work(void *arg) {
  int *i = (int *)arg;

  if (*i == 0) { /* Creation thread */
    if (thrd_success != mtx_init(&lock, mtx_plain)) {
      /* Handle error */
    }
    atomic_store(&completed, 1);
  } else if (*i < max_threads - 1) { /* Worker thread */
    if (thrd_success != mtx_lock(&lock)) {
      /* Handle error */
    }
    /* Access data protected by the lock */
    atomic_fetch_add(&completed, 1);
    if (thrd_success != mtx_unlock(&lock)) {
      /* Handle error */
    }
  } else { /* Destruction thread */
    mtx_destroy(&lock);
  }
  return 0;
}
 
int main(void) {
  thrd_t threads[max_threads];
  
  for (size_t i = 0; i < max_threads; i++) {
    if (thrd_success != thrd_create(&threads[i], do_work, &i)) {
      /* Handle error */
    }
  }
  for (size_t i = 0; i < max_threads; i++) {
    if (thrd_success != thrd_join(threads[i], 0)) {
      /* Handle error */
    }
  }
  return 0;
}
