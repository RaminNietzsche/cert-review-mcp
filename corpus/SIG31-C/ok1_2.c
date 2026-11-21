// corpus: SIG31-C compliant
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

#include <signal.h>
#include <stdlib.h>
#include <string.h>
 
#ifdef __STDC_NO_ATOMICS__
#error "Atomics are not supported"
#endif
 
#include <stdatomic.h>
 
#if ATOMIC_INT_LOCK_FREE == 0
#error "int is never lock-free"
#endif

atomic_int e_flag = 0;
 
void handler(int signum) {
  e_flag = 1;
}

int main(void) {
  enum { MAX_MSG_SIZE = 24 };
  char err_msg[MAX_MSG_SIZE];
#if ATOMIC_INT_LOCK_FREE == 1
  if (!atomic_is_lock_free(&e_flag)) {
    return EXIT_FAILURE;
  }
#endif
  if (signal(SIGINT, handler) == SIG_ERR) {
    return EXIT_FAILURE;
  }
  strcpy(err_msg, "No errors yet.");
  /* Main code loop */
  if (e_flag) {
    strcpy(err_msg, "SIGINT received.");
  }
  return EXIT_SUCCESS;
}
