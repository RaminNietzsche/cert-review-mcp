// corpus: EXP09-C noncompliant
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

int f(void) { /* Assuming 32-bit pointer, 32-bit integer */
  size_t i;
  int **matrix = (int **)calloc(100, 4);
  if (matrix == NULL) {
    return -1; /* Indicate calloc() failure */
  }

  for (i = 0; i < 100; i++) {
    matrix[i] = (int *)calloc(i, 4);
    if (matrix[i] == NULL) {
      return -1; /* Indicate calloc() failure */
    }
  }
 return 0;
}
