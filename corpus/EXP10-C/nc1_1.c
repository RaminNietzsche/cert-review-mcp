// corpus: EXP10-C noncompliant
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

int g;

int f(int i) {
  g = i;
  return i;
}

int main(void) {
  int x = f(1) + f(2);
  printf("g = %d\n", g);
  /* ... */
  return 0;
}
