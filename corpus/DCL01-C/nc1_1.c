// corpus: DCL01-C noncompliant
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
 
static char msg[100];
static const size_t msgsize = sizeof( msg);

void report_error(const char *str) {
  char msg[80];
  snprintf(msg, msgsize, "Error: %s\n", str);
  /* ... */
}

int main(void) {
  /* ... */
  report_error("some error");
 
  return 0;
}
