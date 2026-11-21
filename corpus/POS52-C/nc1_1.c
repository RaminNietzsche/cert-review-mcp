// corpus: POS52-C noncompliant
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

pthread_mutexattr_t attr;
pthread_mutex_t mutex;

void *thread_foo(void *ptr) {
  uint32_t num;
  int result;
  int sock;

  /* sock is a connected TCP socket */

  if ((result = pthread_mutex_lock(&mutex)) != 0) {
    /* Handle Error */
  }

  if ((result = recv(sock, (void *)&num, sizeof(uint32_t), 0)) < 0) {
    /* Handle Error */
  }

  /* ... */

  if ((result = pthread_mutex_unlock(&mutex)) != 0) {
    /* Handle Error */
  }
  return NULL;
}

int main() {
  pthread_t thread;
  int result;

  if ((result = pthread_mutexattr_init(&attr)) != 0) {
    /* Handle Error */
  }

  if ((result = pthread_mutexattr_settype(
      &attr, PTHREAD_MUTEX_ERRORCHECK)) != 0) {
    /* Handle Error */
  }

  if ((result = pthread_mutex_init(&mutex, &attr)) != 0) {
    /* Handle Error */
  }

  if (pthread_create(&thread, NULL, thread_foo, NULL) != 0) {
    /* Handle Error */
  }

  /* ... */

  pthread_join(thread, NULL);

  if ((result = pthread_mutex_destroy(&mutex)) != 0) {
    /* Handle Error */
  }

  return 0;
}
