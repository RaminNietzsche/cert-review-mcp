// corpus: ERR33-C noncompliant
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
 
extern void log_message(const char *);

void f(int i, int width, int prec) {
  char buf[40];
  snprintf(buf, sizeof(buf), "i = %*.*i", width, prec, i);
  log_message(buf);
  /* ... */
}
