// corpus: ERR33-C compliant
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
#include <string.h>
 
extern void log_message(const char *);

void f(int i, int width, int prec) {
  char buf[40];
  int n;
  n = snprintf(buf, sizeof(buf), "i = %*.*i", width, prec, i);
  if (n < 0 || n >= sizeof(buf)) {
    /* Handle snprintf() error */
    strcpy(buf, "unknown error");
  }
  log_message(buf);
}
