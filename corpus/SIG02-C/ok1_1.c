// corpus: SIG02-C compliant
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

#include <pthread.h>

pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
pthread_mutex_t mut = PTHREAD_MUTEX_INITIALIZER;

/* THREAD 1 */
int do_work(void) {
  int result;
  /* ... */
  if ((result = pthread_mutex_lock(&mut)) != 0) {
    /* Handle error condition */
  }
  if ((result = pthread_cond_signal(&cond)) != 0) {
    /* Handle error condition */
  }
  if ((result = pthread_mutex_unlock(&mut)) != 0) {
    /* Handle error condition */
  }
  return 0;
}

/* THREAD 2 */
int wait_and_work(void) {
  int result;
  if ((result = pthread_mutex_lock(&mut)) != 0) {
    /* Handle error condition */
  }
  while (/* Condition does not hold */) {
    if ((result = pthread_cond_wait(&cond, &mut)) != 0) {
      /* Handle error condition */
    }
    /* ... */
  }
  if ((result = pthread_mutex_unlock(&mut)) != 0) {
    /* Handle error condition */
  }
  /* ... */
  return 0;
}
