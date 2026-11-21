// corpus: ENV30-C noncompliant
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

#include <locale.h>
 
void f2(void) {
  struct lconv *conv = localeconv();
 
  if ('\0' == conv->decimal_point[0]) {
    conv->decimal_point = ".";
  }
}
