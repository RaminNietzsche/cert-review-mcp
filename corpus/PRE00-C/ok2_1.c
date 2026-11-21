// corpus: PRE00-C compliant
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

size_t count = 0;

void g(void) {
  printf("Called g, count = %zu.\n", count);
}

typedef void (*exec_func)(void);
inline void exec_bump(exec_func f) {
  f();
  ++count;
}

void aFunc(void) {
  size_t count = 0;
  while (count++ < 10) {
    exec_bump(g);
  }
}
