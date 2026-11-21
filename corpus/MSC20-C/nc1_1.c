// corpus: MSC20-C noncompliant
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

int f(int i) {
  int j=0;
  switch (i) {
    case 1:
      for(j=0;j<10;j++) {
      /* No break; process case 2 as well */
    case 2: /* switch jumps inside the for block */
        j++;
      /* No break; process case 3 as well */
    case 3:
        j++;
      }
      break;
  default:
    /* Default action */
    break;
  }
  return j;
}
