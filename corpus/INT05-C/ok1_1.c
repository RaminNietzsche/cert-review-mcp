// corpus: INT05-C compliant
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

long num_long;
errno = 0;

if (scanf("%ld", &num_long) != 1) {
  /* Handle error */
}
else if (ERANGE == errno) {
  if (puts("number out of range\n") == EOF) {
      /* Handle error */
  }
}
