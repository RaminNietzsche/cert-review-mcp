// corpus: SIG35-C noncompliant
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

#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <stdlib.h>

volatile sig_atomic_t denom;

void sighandle(int s) {
  /* Fix the offending volatile */
  if (denom == 0) {
    denom = 1;
  }
}

int main(int argc, char *argv[]) {
  if (argc < 2) {
    return 0;
  }
 
  char *end = NULL;
  long temp = strtol(argv[1], &end, 10);
 
  if (end == argv[1] || 0 != *end ||
      ((LONG_MIN == temp || LONG_MAX == temp) && errno == ERANGE)) {
    /* Handle error */
  }
 
  denom = (sig_atomic_t)temp;
  signal(SIGFPE, sighandle);

  long result = 100 / (long)denom;
  return 0;
}
