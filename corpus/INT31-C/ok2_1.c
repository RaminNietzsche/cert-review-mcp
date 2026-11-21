// corpus: INT31-C compliant
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

#include <limits.h>

void func(signed int si) {
  unsigned int ui;
  if (si < 0) {
    /* Handle error */
  } else {
    ui = (unsigned int)si;  /* Cast eliminates warning */
  }
  /* ... */
}
/* ... */

func(INT_MIN + 1);
