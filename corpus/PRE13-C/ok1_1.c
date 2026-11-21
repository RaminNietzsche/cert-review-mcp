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

#include <stdio.h>

int main(void) {
  #if defined(__STDC__)
    #if (__STDC__ == 1)
      printf("Implementation is ISO-conforming.\n");
    #else
      printf("Implementation is not ISO-conforming.\n");
    #endif
  #else   /* !defined(__STDC__) */
    printf("__STDC__ is not defined.\n");
  #endif
  /* ... */
  return 0;
}
