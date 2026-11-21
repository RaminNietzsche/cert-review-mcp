// corpus: DCL17-C compliant
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

int vol_read_int(volatile int *vp) {
  return *vp;
}
volatile int *vol_id_int(volatile int *vp) {
  return vp;
}

const volatile int x;
volatile int y;
void foo(void) {
  for(*vol_id_int(&y) = 0; vol_read_int(&y) < 10; *vol_id_int(&y) = vol_read_int(&y) + 1) {
    int z = vol_read_int(&x);
  }
}
