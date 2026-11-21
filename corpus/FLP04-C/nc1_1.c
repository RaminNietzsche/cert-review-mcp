// corpus: FLP04-C noncompliant
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

float currentBalance; /* User's cash balance */
void doDeposit() {
  float val;

  scanf("%f", &val);

  if(val >= MAX_VALUE - currentBalance) {
    /* Handle range error */
  }

  currentBalance += val;
}
