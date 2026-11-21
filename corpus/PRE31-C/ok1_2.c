// corpus: PRE31-C compliant
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

#include <complex.h>
#include <math.h>
 
static inline int iabs(int x) {
  return (((x) < 0) ? -(x) : (x));
}
 
void func(int n) {
  /* Validate that n is within the desired range */

int m = iabs(++n);

  /* ... */
}
