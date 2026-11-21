// corpus: CON37-C compliant
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
#include <stdbool.h>
#include <stddef.h>
#include <threads.h>
 
atomic_bool flag = false;

int func(void *data) {
  while (!flag) {
    /* ... */
  }
  return 0;
}

int main(void) {
  thrd_t tid;
  
  if (thrd_success != thrd_create(&tid, func, NULL)) {
    /* Handle error */
  }
  /* ... */
  /* Set flag when done */
  flag = true;

  return 0;
}
