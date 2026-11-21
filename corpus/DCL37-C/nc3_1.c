// corpus: DCL37-C noncompliant
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

#include <inttypes.h>
#include <stdio.h>

static const int_fast16_t INTFAST16_LIMIT_MAX = 12000;

void print_fast16(int_fast16_t val) {
  enum { SIZE_MAX = 80 };
  char buf[SIZE_MAX];
  if (INTFAST16_LIMIT_MAX < val) {
    sprintf(buf, "The value is too large");
  } else {
    snprintf(buf, SIZE_MAX, "The value is %" PRIdFAST16, val);
  }
}
