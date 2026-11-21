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

#include <setjmp.h>

const errno_t ESOMETHINGREALLYBAD = 1;

jmp_buf exception_env;

void g(void) {
  /* ... */
  if (something_really_bad_happens) {
    longjmp(exception_env, ESOMETHINGREALLYBAD);
  }
  /* ... */
}

void f(void) {
  g();
  /* ... Do the rest of f ... */
}

/* ... */
if (setjmp(exception_env) != 0) {
  /*
   * If we get here, an error occurred; 
   * do not continue processing.
   */
}
/* ... */
f();
/* If we get here, no errors occurred */
/* ... */
