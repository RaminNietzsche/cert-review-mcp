// corpus: EXP11-C compliant
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

struct bf {
  unsigned int m1 : 6;
  unsigned int m2 : 4;
};

void function() {
  struct bf data;
  data.m1 = 0;
  data.m2 = 0;
  data.m2 += 1;
}
