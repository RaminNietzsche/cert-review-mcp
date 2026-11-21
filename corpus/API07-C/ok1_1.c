// corpus: API07-C compliant
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

char *source;
char a[NTBS_SIZE];
/* ... */
if (source) {
  errno_t err = strncpy_s(a, sizeof(a), source, 5);
  if (err != 0) {
    /* Handle error */
  }
}
else {
  /* Handle null string condition */
}
