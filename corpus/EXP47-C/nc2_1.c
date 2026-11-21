// corpus: EXP47-C noncompliant
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

#include <stdarg.h>
 
void func(const char *cp, ...) {
  va_list ap;  
  va_start(ap, cp);
  int val = va_arg(ap, int);
  // ...
  va_end(ap);
}
 
void f(void) {
  func("The only argument");
}
