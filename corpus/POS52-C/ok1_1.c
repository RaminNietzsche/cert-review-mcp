// corpus: POS52-C compliant
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

void *thread_foo(void *ptr) {
  uint32_t num;
  int result;
  int sock;

  /* sock is a connected TCP socket */

  if ((result = recv(sock, (void *)&num, sizeof(uint32_t), 0)) < 0) {
    /* Handle Error */
  }

  if ((result = pthread_mutex_lock(&mutex)) != 0) {
    /* Handle Error */
  }

  /* ... */

  if ((result = pthread_mutex_unlock(&mutex)) != 0) {
    /* Handle Error */
  }
  return NULL;
}
