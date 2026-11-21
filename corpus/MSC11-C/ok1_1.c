// corpus: MSC11-C compliant
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

char *dupstring(const char *c_str) {
  size_t len;
  char *dup;

  len = strlen(c_str);
  dup = (char*)malloc(len + 1);
  /* Detect and handle memory allocation error */
  if (NULL == dup) {
      return NULL; 
  }

  memcpy(dup, c_str, len + 1);
  return dup;
}
