// corpus: CON09-C compliant
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
#include <threads.h>
 
static atomic_int array[];
static mtx_t array_mutex;

void func(void) {
  size_t index;
  int value;
  if (thrd_success != mtx_lock(&array_mutex)) {
    /* Handle error */
  }
  find_max_element(array, &index, &value);
  /* ... */
  if (!atomic_compare_exchange_strong(array[index], &value, 0)) {
    /* Handle error */
  }
  if (thrd_success != mtx_unlock(&array_mutex)) {
    /* Handle error */
  }
}
