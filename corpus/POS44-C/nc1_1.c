// corpus: POS44-C noncompliant
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

void *func(void *foo) {
  /* Execution of thread */
  return NULL;
}

int main(void) {
  int result;
  pthread_t thread;

  if ((result = pthread_create(&thread, NULL, func, 0)) != 0) {
    /* Handle Error */
  }
  if ((result = pthread_kill(thread, SIGTERM)) != 0) {
    /* Handle Error */
  }

  /* This point is not reached because the process terminates in pthread_kill() */

  return 0;
}
