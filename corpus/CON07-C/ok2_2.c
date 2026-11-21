// corpus: CON07-C compliant
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
#include <stdbool.h>

static int a;
static int b;
mtx_t flag_mutex;

/* Initialize everything */
bool init_all(int type) {
  /* Check mutex type */
  a = 0;
  b = 0;
  if (thrd_success != mtx_init(&flag_mutex, type)) {
    return false;  /* Report error */
  }
  return true;
}
 
int get_sum(void) {
  if (thrd_success != mtx_lock(&flag_mutex)) {
    /* Handle error */
  }
  int sum = a + b;
  if (thrd_success != mtx_unlock(&flag_mutex)) {
    /* Handle error */
  }
  return sum;
}
 
void set_values(int new_a, int new_b) {
  if (thrd_success != mtx_lock(&flag_mutex)) {
    /* Handle error */
  }
  a = new_a;
  b = new_b;
  if (thrd_success != mtx_unlock(&flag_mutex)) {
    /* Handle error */
  }
}
