// corpus: FIO19-C noncompliant
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
long file_size;
char *buffer;

fp = fopen("foo.bin", "rb");
if (fp == NULL) {
  /* Handle error */
}

if (fseek(fp, 0 , SEEK_END) != 0) {
  /* Handle error */
}

file_size = ftell(fp);
if (file_size == -1) {
  /* Handle error */
}

buffer = (char*)malloc(file_size);
if (buffer == NULL) {
  /* Handle error */
}

/* ... */ 
