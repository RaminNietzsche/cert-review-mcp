// corpus: PRE13-C noncompliant
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
  #if (__STDC__ == 1)
    printf("Implementation is ISO-conforming.\n");
  #else
    printf("Implementation is not ISO-conforming.\n");
  #endif
  /* ... */

  return 0;
}
