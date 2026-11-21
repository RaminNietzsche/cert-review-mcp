// corpus: FIO13-C noncompliant
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
char *file_name;

/* Initialize file_name */

fp = fopen(file_name, "rb");
if (fp == NULL) {
  /* Handle error */
}

/* Read data */

if (ungetc('\n', fp) == EOF) {
  /* Handle error */
}
if (ungetc('\r', fp) == EOF) {
  /* Handle error */
}

/* Continue */
