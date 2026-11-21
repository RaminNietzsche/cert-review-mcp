// corpus: FIO09-C compliant
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

struct myData {
  char c;
  long l;
};

/* ... */

FILE *file;
struct myData data;
char buf[25];
char *end_ptr;

/* Initialize file */

if (fgets(buf, sizeof(buf), file) == NULL) {
  /* Handle error */
}

data.c = buf[0];

if (fgets(buf, sizeof(buf), file) == NULL) {
  /* Handle Error */
}

data.l = strtol(buf, &end_ptr, 10);

if ((ERANGE == errno)
 || (end_ptr == buf)
 || ('\n' != *end_ptr && '\0' != *end_ptr)) {
    /* Handle Error */
}
