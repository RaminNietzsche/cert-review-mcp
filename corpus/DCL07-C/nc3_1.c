// corpus: DCL07-C noncompliant
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

int add(int x, int y, int z) {
  return x + y + z;
}

int main(int argc, char *argv[]) {
  int (*fn_ptr) (int, int);
  int res;
  fn_ptr = add;
  res = fn_ptr(2, 3);  /* Incorrect */
  /* ... */
  return 0;
}
