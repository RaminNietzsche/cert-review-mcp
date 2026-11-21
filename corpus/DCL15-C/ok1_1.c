// corpus: DCL15-C compliant
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

enum {MAX = 100};

static int helper(int i) {
  /* Perform some computation based on i */
}

int main(void) {
  size_t i;
  int out[MAX];

  for (i = 0; i < MAX; i++) {
    out[i] = helper(i);
  }

  /* ... */

}
