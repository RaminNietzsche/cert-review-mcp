// corpus: SIG02-C noncompliant
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

/* THREAD 1 */
int do_work(void) {
  /* ... */
  kill(THR2_PID, SIGUSR1);
}

/* THREAD 2 */
volatile sig_atomic_t flag;

void sigusr1_handler(int signum) {
  flag = 1;
}

int wait_and_work(void) {
  flag = 0;
  while (!flag) {}
  /* ... */
}
