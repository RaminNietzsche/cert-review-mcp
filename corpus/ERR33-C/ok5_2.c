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
#include <stdlib.h>
#include <string.h>

extern void log_message(const char *);

void f(int i, int width, int prec) {
  char buffer[20];
  char *buf = buffer;
  int n  = sizeof(buffer);
  const char fmt[] = "i = %*.*i";

  n = snprintf(buf, 0, fmt, width, prec, i); // obtain size
  if (n < 0) {
    /* Handle snprintf() error */
    strcpy(buffer, "unknown error");
    goto write_log;
  }

  if ((size_t)n >= sizeof(buffer)) {
    buf = (char *)malloc((size_t)n + 1);
    if (NULL == buf) {
      /* Handle malloc() error */
      buf = buffer;
      strcpy(buffer, "unknown error");
      goto write_log;
    }
  }

  n = snprintf(buf, (size_t)n + 1, fmt, width, prec, i);
  if (n < 0) {
    /* Handle snprintf() error */
    strcpy(buf, "unknown error");
  }

write_log:
  log_message(buf);

  if (buf != buffer) {
    free(buf);
  }
}
