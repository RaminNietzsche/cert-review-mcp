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

void g(errno_t * err) {
  if (err == NULL) {
    /* Handle null pointer */
  }
  /* ... */
  if (something_really_bad_happens) {
    *err = ESOMETHINGREALLYBAD;
  } else {
    /* ... */
    *err = 0;
  }
}

void f(errno_t * err) {
  if (err == NULL) {
    /* Handle null pointer */
  }
  g(err);
  if (*err == 0) {
    /* ... Do the rest of f ... */
  }
  return 0;
}
