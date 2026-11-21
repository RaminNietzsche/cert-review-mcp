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
 
void func(double x) {
  double result;

  if (isless(x, 0.0)) {
    /* Handle domain error */
  }

  result = sqrt(x);

  /* Use result... */
}
