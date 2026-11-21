// corpus: EXP44-C noncompliant
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

#define S(val) _Generic(val, int : 2, \
                             short : 3, \
                             default : 1)
void func(void) {
  int a = 0;
  int b = S(a++);
  printf("%d, %d\n", a, b);
}
