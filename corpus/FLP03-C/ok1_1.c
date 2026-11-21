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

#include <fenv.h>
#pragma STDC FENV_ACCESS ON

void fpOper_fenv(void) {
  double a = 1e-40, b, c = 0.1;
  float x = 0, y;
  int fpeRaised;
  /* ... */

  feclearexcept(FE_ALL_EXCEPT);
  /* Store a into y is inexact and underflows: */
  y = a;
  fpeRaised = fetestexcept(FE_ALL_EXCEPT);
  /* fpeRaised has FE_INEXACT and FE_UNDERFLOW */

  feclearexcept(FE_ALL_EXCEPT);

  /* Divide-by-zero operation */
  b = y / x;
  fpeRaised = fetestexcept(FE_ALL_EXCEPT);
  /* fpeRaised has FE_DIVBYZERO */

  feclearexcept(FE_ALL_EXCEPT);

  c = sin(30) * a;
  fpeRaised = fetestexcept(FE_ALL_EXCEPT);
  /* fpeRaised has FE_INEXACT */

  feclearexcept(FE_ALL_EXCEPT);
  /* ... */
}
