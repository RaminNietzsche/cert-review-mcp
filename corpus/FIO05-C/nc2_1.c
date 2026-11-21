// corpus: FIO05-C noncompliant
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
FILE *fd;

/* Initialize file_name */

fd = fopen(file_name, "r+");
if (fd == NULL) {
  /* Handle error */
}

/* Read user's file */

fclose(fd);
fd = NULL; 
