// corpus: INT32-C compliant
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

#include <stdckdint.h>

void func(signed int si_a, signed int si_b) {
  int product;
  if (ckd_mul(&product, si_a, si_b)) {
    /* Handle error */
  }
  /* ... */
}
