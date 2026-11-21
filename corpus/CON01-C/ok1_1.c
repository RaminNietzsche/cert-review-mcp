// corpus: CON01-C compliant
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

enum { MIN_BALANCE = 50 };

static int account_balance;
static mtx_t mp;

/* Initialize mp */

static int verify_balance(int amount) {
  if (account_balance - amount < MIN_BALANCE) {
    return -1;   /* Indicate error to caller */
  }

  return 0;  /* Indicate success to caller */
}

int debit(int amount) {
  if (mtx_lock(&mp) == thrd_error) {
    return -1;   /* Indicate error to caller */
  }

  if (verify_balance(amount)) {
    mtx_unlock(&mp);
    return -1;   /* Indicate error to caller */
  }

  account_balance -= amount;

  if (mtx_unlock(&mp) == thrd_error) {
    return -1;   /* Indicate error to caller */
  }

  return 0;   /* Indicate success */
}
