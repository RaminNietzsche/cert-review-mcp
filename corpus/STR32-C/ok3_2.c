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
    if (strnlen(source, sizeof(c_str)) < sizeof(c_str)) {
      strcpy(c_str, source);
      ret = strlen(c_str);
    } else {
      /* Handle string-too-large */
    }
  } else {
    /* Handle null pointer */
  }
  return ret;
}
