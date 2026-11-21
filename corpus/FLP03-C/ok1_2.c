// corpus: FLP03-C compliant
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

void fpOper_usingStatus(void) {
  /* ... */
  double a = 1e-40, b, c;
  float x = 0, y;
  unsigned int rv = _clearfp();

  /* Store into y is inexact and underflows: */
  y = a;
  rv = _clearfp();  /* rv has _SW_INEXACT and _SW_UNDERFLOW */

  /* Zero-divide */
  b = y / x; rv = _clearfp(); /* rv has _SW_ZERODIVIDE */

  /* Inexact */
  c = sin(30) * a; rv = _clearfp(); /* rv has _SW_INEXACT */
  /* ... */
}
