// corpus: PRE10-C noncompliant
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

if (x > y) { /* Single-branch if-statement!!! */

  tmp = x;   /* The one and only branch consists */
  x = y;     /* of the block. */
  y = tmp;
}
;            /* Empty statement */
else         /* ERROR!!! "parse error before else" */
  do_something();
