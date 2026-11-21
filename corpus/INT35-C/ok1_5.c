// corpus: INT35-C compliant
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

unsigned int pow2(unsigned int exp) {
  if (exp >= UINT_WIDTH) {
    /* Handle error */
  }
  return 1 << exp;
}
