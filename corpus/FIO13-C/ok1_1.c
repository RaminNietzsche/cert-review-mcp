// corpus: FIO13-C compliant
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

FILE *fp;
fpos_t pos;
char *file_name;

/* Initialize file_name */

fp = fopen(file_name, "rb");
if (fp == NULL) {
  /* Handle error */
}

/* Read data */

if (fgetpos(fp, &pos)) {
  /* Handle error */
}

/* Read the data that will be "pushed back" */

if (fsetpos(fp, &pos)) {
  /* Handle error */
}

/* Continue */
