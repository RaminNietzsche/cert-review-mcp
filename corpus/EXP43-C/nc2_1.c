// corpus: EXP43-C noncompliant
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
void f(size_t n, int *restrict p, const int *restrict q) {
  while (n-- > 0) {
    *p++ = *q++;
  }
}
 
void g(void) {
  extern int d[100];
  /* ... */
  f(50, d + 1, d); /* Undefined behavior */
}
