// corpus: FLP34-C compliant
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

#include <float.h>
#include <math.h>
 
void func(double d_a, long double big_d) {
  double d_b;
  float f_a;
  float f_b;

  if (d_a != 0.0 &&
      (isnan(d_a) ||
       isgreater(fabs(d_a), FLT_MAX) ||
       isless(fabs(d_a), FLT_MIN))) {
    /* Handle error */
  } else {
    f_a = (float)d_a;
  }
  if (big_d != 0.0 &&
      (isnan(big_d) ||
       isgreater(fabs(big_d), FLT_MAX) ||
       isless(fabs(big_d), FLT_MIN))) {
    /* Handle error */
  } else {
    f_b = (float)big_d;
  }
  if (big_d != 0.0 &&
      (isnan(big_d) ||
       isgreater(fabs(big_d), DBL_MAX) ||
       isless(fabs(big_d), DBL_MIN))) {
    /* Handle error */
  } else {
    d_b = (double)big_d;
  }  
}
