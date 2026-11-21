// corpus: POS53-C compliant
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

#include <stdio.h>
#include <pthread.h>
 
pthread_mutex_t mutex1; /* Initialized as PTHREAD_MUTEX_ERRORCHECK */
pthread_cond_t cv;
int count1 = 0, count2 = 0;
#define COUNT_LIMIT 5

void *waiter1() {
  int ret;
  while (count1 < COUNT_LIMIT) {
    if ((ret = pthread_mutex_lock(&mutex1)) != 0) {
      /* Handle error */
    }

    if ((ret = pthread_cond_wait(&cv, &mutex1)) != 0) {
      /* Handle error */
    }

    printf("count1 = %d\n", ++count1);

    if ((ret = pthread_mutex_unlock(&mutex1)) != 0) {
      /* Handle error */
    }
  }

  return NULL;
}

void *waiter2() {
  int ret;
  while (count2 < COUNT_LIMIT) {
    if ((ret = pthread_mutex_lock(&mutex1)) != 0) {
      /* Handle error */
    }

    if ((ret = pthread_cond_wait(&cv, &mutex1)) != 0) {
      /* Handle error */
    }

    printf("count2 = %d\n", ++count2);

    if ((ret = pthread_mutex_unlock(&mutex1)) != 0) {
      /* Handle error */
    }
  }

  return NULL;
}
