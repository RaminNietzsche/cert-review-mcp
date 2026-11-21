// corpus: FIO42-C noncompliant
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

#include <stdio.h>
 
int func(const char *filename) {
  FILE *f = fopen(filename, "r"); 
  if (NULL == f) {
    return -1;
  }
  /* ... */
  return 0;
}
