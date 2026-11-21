// corpus: FLP03-C noncompliant
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

void fpOper_noErrorChecking(void) {
  /* ... */
  double a = 1e-40, b, c = 0.1;
  float x = 0, y;
  /* Inexact and underflows */
  y = a;
  /* Divide-by-zero operation */
  b = y / x;
  /* Inexact (loss of precision) */
  c = sin(30) * a;
  /* ... */
}
