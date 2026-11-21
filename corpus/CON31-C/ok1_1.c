// corpus: CON31-C compliant
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
/* Atomic so multiple threads can increment safely */
atomic_int completed = 0;
enum { max_threads = 5 }; 

int do_work(void *dummy) {
  if (thrd_success != mtx_lock(&lock)) {
    /* Handle error */
  }
  /* Access data protected by the lock */
  atomic_fetch_add(&completed, 1);
  if (thrd_success != mtx_unlock(&lock)) {
    /* Handle error */
  }

  return 0;
}

int main(void) {
  thrd_t threads[max_threads];
  
  if (thrd_success != mtx_init(&lock, mtx_plain)) {
    /* Handle error */
  }
  for (size_t i = 0; i < max_threads; i++) {
    if (thrd_success != thrd_create(&threads[i], do_work, NULL)) {
      /* Handle error */
    }
  }
  for (size_t i = 0; i < max_threads; i++) {
    if (thrd_success != thrd_join(threads[i], 0)) {
      /* Handle error */
    }
  }

  mtx_destroy(&lock);
  return 0;
}
