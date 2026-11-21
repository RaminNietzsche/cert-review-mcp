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
 
static bool flag = false;
mtx_t flag_mutex;

/* Initialize flag_mutex */
bool init_mutex(int type) {
  /* Check mutex type */
  if (thrd_success != mtx_init(&flag_mutex, type)) {
    return false;  /* Report error */
  }
  return true;
}
 
void toggle_flag(void) {
  if (thrd_success != mtx_lock(&flag_mutex)) {
    /* Handle error */
  }
  flag = !flag;
  if (thrd_success != mtx_unlock(&flag_mutex)) {
    /* Handle error */
  }
}
 
bool get_flag(void) {
  bool temp_flag;
  if (thrd_success != mtx_lock(&flag_mutex)) {
    /* Handle error */
  }
  temp_flag = flag;
  if (thrd_success != mtx_unlock(&flag_mutex)) {
    /* Handle error */
  }
  return temp_flag;
}
