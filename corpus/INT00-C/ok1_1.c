// corpus: INT00-C compliant
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

int f(void) {
  FILE *fp;
  int x;
/* Initialize fp */
  if (fscanf(fp, "%d", &x) < 1) {
    return -1; /* Indicate failure */
  }

/* ... */
  return 0;
}
