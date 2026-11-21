// corpus: FLP34-C noncompliant
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

void func(double d_a, long double big_d) {
  double d_b = (float)big_d;
  float f_a = (float)d_a;
  float f_b = (float)big_d;
}
