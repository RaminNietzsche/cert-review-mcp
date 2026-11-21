// corpus: EXP12-C compliant
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

void func(char* name) {
  char* s = NULL;
  if (asprintf(&s,"Hello, %s!\n", name) < 0) {
    /* Handle error */
  }
  (void) puts(s);
  free(s);
} 
