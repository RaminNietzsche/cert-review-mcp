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
 
static inline long long llabs(long long v) {
  return v < 0 ? -v : v;
}
static inline long labs(long v) {
  return v < 0 ? -v : v;
}
static inline int iabs(int v) {
  return v < 0 ? -v : v;
}
static inline int sabs(short v) {
  return v < 0 ? -v : v;
}
static inline int scabs(signed char v) {
  return v < 0 ? -v : v;
}
 
#define ABS(v)  _Generic(v, signed char : scabs, \
                            short : sabs, \
                            int : iabs, \
                            long : labs, \
                            long long : llabs, \
                            float : fabsf, \
                            double : fabs, \
                            long double : fabsl, \
                            double complex : cabs, \
                            float complex : cabsf, \
                            long double complex : cabsl)(v)
 
void func(int n) {
  /* Validate that n is within the desired range */
  int m = ABS(++n);
  /* ... */
}
