// corpus: INT01-C noncompliant
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

char *copy(size_t n, const char *c_str) {
  int i;
  char *p;

  if (n == 0) {
    /* Handle unreasonable object size error */
  }
  p = (char *)malloc(n);
  if (p == NULL) {
    return NULL; /* Indicate malloc failure */
  }
  for ( i = 0; i < n; ++i ) {
    p[i] = *c_str++;
  }
  return p;
}

/* ... */

char c_str[] = "hi there";
char *p = copy(sizeof(c_str), c_str);
