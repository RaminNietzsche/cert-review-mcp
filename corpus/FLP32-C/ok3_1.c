// corpus: FLP32-C compliant
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

#include <math.h>
#include <fenv.h>
#include <errno.h>
 
void func(double x, double y) {
  double result;

  if (((x == 0.0f) && islessequal(y, 0.0)) || isless(x, 0.0)) {
    /* Handle domain or pole error */
  }

  {
    #pragma STDC FENV_ACCESS ON
    if (math_errhandling & MATH_ERREXCEPT) {
      feclearexcept(FE_ALL_EXCEPT);
    }
    errno = 0;

    result = pow(x, y);
 
    if ((math_errhandling & MATH_ERRNO) && errno != 0) {
      /* Handle range error */
    } else if ((math_errhandling & MATH_ERREXCEPT) &&
               fetestexcept(FE_INVALID | FE_DIVBYZERO |
                            FE_OVERFLOW | FE_UNDERFLOW) != 0) {
      /* Handle range error */
    }
  }

  /* Use result... */
}
