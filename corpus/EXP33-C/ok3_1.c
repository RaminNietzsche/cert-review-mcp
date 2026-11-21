// corpus: EXP33-C compliant
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
  char buffer[BUFFERSIZE];

  if (0 < snprintf(buffer, BUFFERSIZE, "Error: %s", msg))
    printf("%s\n", buffer);
  else
    puts("Unknown error");
}
