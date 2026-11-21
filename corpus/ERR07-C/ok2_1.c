// corpus: ERR07-C compliant
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

char *file_name;
FILE *fp;

/* Initialize file_name */

fp = fopen(file_name, "r");
if (fp == NULL) {
  /* Handle open error */
}

/* Read data */

if (fseek(fp, 0L, SEEK_SET) != 0) {
  /* Handle repositioning error */
}

/* Continue */
