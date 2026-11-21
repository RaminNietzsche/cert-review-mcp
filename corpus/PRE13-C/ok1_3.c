// corpus: PRE13-C compliant
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

#if defined(__STDC_LIB_EXT1__)
  #if (__STDC_LIB_EXT1__ >= 201112L)
    #define USE_EXT1 1
    #define __STDC_WANT_LIB_EXT1__ 1 /* Want the ext1 functions */
  #endif
#endif
 
#include <string.h>
#include <stdlib.h>
 
int main(void) {
  char source_msg[] = "This is a test.";
  char *msg = malloc(sizeof(source_msg) + 1);
 
  if (msg != NULL) {
    #if defined(USE_EXT1)
      strcpy_s(msg, sizeof(source_msg) + 1, source_msg);
    #else
      strcpy(msg, source_msg);
    #endif
  } 
  else {
    return EXIT_FAILURE;
  }
  return 0;
}
