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

errno_t my_errno; /* Also declared in a .h file */
const errno_t ESOMETHINGREALLYBAD = 1;

void g(void) {
  /* ... */
  if (something_really_bad_happens) {
    my_errno = ESOMETHINGREALLYBAD;
    return;
  }
  /* ... */
}

void f(void) {
  my_errno = 0;
  g();
  if (my_errno != 0) {
    return;
  }
  /* ... Do the rest of f ... */
}
