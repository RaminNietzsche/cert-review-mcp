// corpus: MSC15-C compliant
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

#include <assert.h>
#include <limits.h>
#include <stdio.h>

int foo(int a) {
  assert(a < (INT_MAX - 100));
  printf("%d %d\n", a + 100, a);
  return a;
}

int main(void) {
  foo(100);
  foo(INT_MAX);
  return 0;
}
