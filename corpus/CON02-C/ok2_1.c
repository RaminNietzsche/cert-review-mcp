// corpus: CON02-C compliant
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

int account_balance;
mtx_t flag;

/* Initialize flag */

int debit(unsigned int amount) {
  if (mtx_lock(&flag) == thrd_error) {
    return -1;  /* Indicate error */
  }
 
  account_balance -= amount; /* Inside critical section */

  if (mtx_unlock(&flag) == thrd_error) {
    return -1;  /* Indicate error */
  }

  return 0;
}
