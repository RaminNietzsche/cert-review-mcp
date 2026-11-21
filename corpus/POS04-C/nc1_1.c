// corpus: POS04-C noncompliant
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
size_t const shared_var = 0;

int main(void) {
  int result;

  if ((result = pthread_mutexattr_init(&attr)) != 0) {
    /* Handle Error */
  }
  if ((result = pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_NORMAL)) != 0) {
    /* Handle Error */
  }
  if ((result = pthread_mutex_init(&mutex, &attr)) != 0) {
    /* Handle Error */
  }
  if ((result = pthread_mutex_lock(&mutex)) != 0) {
    /* Handle Error */
  }

  /* Critical Region*/

  if ((result = pthread_mutex_unlock(&mutex)) != 0) {
    /* Handle Error */
  }

  return 0;
}
