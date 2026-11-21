// corpus: MSC22-C noncompliant
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

jmp_buf buf;

void f(void) {
  int i = setjmp(buf);
  if (i == 0) {
    g();
  } else {
    /* longjmp was invoked */
  }
}

void g(void) {
  /* ... */
  longjmp(buf, 1);
}
