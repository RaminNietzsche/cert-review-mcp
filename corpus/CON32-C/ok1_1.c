// corpus: CON32-C compliant
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

#include <threads.h>
 
struct multi_threaded_flags {
  unsigned int flag1 : 2;
  unsigned int flag2 : 2;
};

struct mtf_mutex {
  struct multi_threaded_flags s;
  mtx_t mutex;
};

struct mtf_mutex flags;

int thread1(void *arg) {
  if (thrd_success != mtx_lock(&flags.mutex)) {
    /* Handle error */
  }
  flags.s.flag1 = 1;
  if (thrd_success != mtx_unlock(&flags.mutex)) {
    /* Handle error */
  }
  return 0;
}
 
int thread2(void *arg) {
  if (thrd_success != mtx_lock(&flags.mutex)) {
    /* Handle error */
  }
  flags.s.flag2 = 2;
  if (thrd_success != mtx_unlock(&flags.mutex)) {
    /* Handle error */
  }
  return 0;
}
