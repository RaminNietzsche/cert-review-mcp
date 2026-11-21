// corpus: PRE30-C noncompliant
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

#define assign(uc1, uc2, val) uc1##uc2 = val

void func(void) {
  int \u0401;
  /* ... */
  assign(\,u0401, 4);
  /* ... */
}
