// corpus: MSC21-C compliant
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

void f(size_t begin, size_t step) {
  if (0 < step) {
    size_t i;
    for (i = begin; i <= SIZE_MAX - step; i += step) {
      /* ... */
    }
  }
}
