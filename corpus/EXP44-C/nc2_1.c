// corpus: EXP44-C noncompliant
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
#include <stdio.h>
  
void f(size_t n) {
  /* n must be incremented */ 
  size_t a = sizeof(int[++n]);
 
  /* n need not be incremented */
  size_t b = sizeof(int[++n % 1 + 1]);

  printf("%zu, %zu, %zu\n", a, b, n);
  /* ... */
}
