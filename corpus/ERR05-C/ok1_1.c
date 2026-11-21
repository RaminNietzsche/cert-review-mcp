// corpus: ERR05-C compliant
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

const errno_t ESOMETHINGREALLYBAD = 1;

errno_t g(void) {
  /* ... */
  if (something_really_bad_happens) {
    return ESOMETHINGREALLYBAD;
  }
  /* ... */
  return 0;
}

errno_t f(void) {
  errno_t status = g();
  if (status != 0) {
    return status;
  }

  /* ... Do the rest of f ... */

  return 0;
}
