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

volatile sig_atomic_t xfer_aborted = 0;

static void myoob(signo) {
  /* ... */
  if (strcmp(cp, "ABOR\r\n") == 0) {
    xfer_aborted = 1;
  }
  /* ... */
}
