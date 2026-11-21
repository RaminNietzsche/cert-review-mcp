// corpus: EXP33-C noncompliant
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
enum { BUFFERSIZE = 24 }; 
void report_error(const char *msg) {
  const char *error_log = msg;
  char buffer[BUFFERSIZE];

  sprintf(buffer, "Error: %s", error_log);
  printf("%s\n", buffer);
}
