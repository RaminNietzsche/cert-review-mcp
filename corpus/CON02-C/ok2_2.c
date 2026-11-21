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

#include <Windows.h>

static volatile LONG account_balance;
CRITICAL_SECTION flag;

/* Initialize flag */
InitializeCriticalSection(&flag);
 
int debit(unsigned int amount) {
  EnterCriticalSection(&flag); 
  account_balance -= amount; /* Inside critical section */
  LeaveCriticalSection(&flag);
 
  return 0;
}
