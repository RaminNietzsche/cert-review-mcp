// corpus: ENV32-C noncompliant
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

#include <stdlib.h>
#include <setjmp.h>

jmp_buf env;
int val;

void exit1(void) {
  longjmp(env, 1);
}

int main(void) {
  if (atexit(exit1) != 0) {
    /* Handle error */
  }
  if (setjmp(env) == 0) {
    exit(0);
  } else {
    return 0;
  }
}
