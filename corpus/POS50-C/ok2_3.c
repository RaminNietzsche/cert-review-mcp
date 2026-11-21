// corpus: POS50-C compliant
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

void *childThread(void *val) {
  /* Correctly prints 1 */
  int *res = (int *)val;
  printf("Result: %d\n", *res);
  return NULL;
}

void createThread(pthread_t *tid, int *val) {
  int result = pthread_create(tid, NULL, childThread, val);
  if (result != 0) {
    /* Handle error */
  }
}

int main(void) {
  /* Declare val in the same function as pthread_join */
  int val = 1;
  int result;
  pthread_t tid;
  createThread(&tid, &val);
  if ((result = pthread_join(tid, NULL)) != 0) {
    /* Handle error */
  }
  return 0;
}
