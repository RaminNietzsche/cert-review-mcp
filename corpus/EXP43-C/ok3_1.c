// corpus: EXP43-C compliant
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

#include <stddef.h>
void add(size_t n, int *restrict res, const int *restrict lhs,
         const int *restrict rhs) {
  for (size_t i = 0; i < n; ++i) {
    res[i] = lhs[i] + rhs[i];
  }
}
 
void f(void) {
   int a[100]; 
   int b[100];
   add(100, a, b, b); /* Defined behavior  */
}
