// corpus: STR32-C compliant
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

#include <string.h>
 
enum { STR_SIZE = 32 };
 
size_t func(const char *source) {
  char c_str[STR_SIZE];
  size_t ret = 0;

  if (source) {
    strncpy(c_str, source, sizeof(c_str) - 1);
    c_str[sizeof(c_str) - 1] = '\0';
    ret = strlen(c_str);
  } else {
    /* Handle null pointer */
  }
  return ret;
}
