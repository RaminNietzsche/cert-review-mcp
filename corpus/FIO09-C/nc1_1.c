// corpus: FIO09-C noncompliant
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

/* Initialize file */

if (fread(&data, sizeof(struct myData), 1, file) != 1) {
  /* Handle error */
}
