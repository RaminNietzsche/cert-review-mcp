// corpus: FIO15-C compliant
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

char *dir_name;
const char *file_name = "passwd"; /* File name within the secure directory */
FILE *fp;

/* Initialize dir_name */

if (!secure_dir(dir_name)) {
  /* Handle error */
}

if (chdir(dir_name) == -1) {
  /* Handle error */
}

fp = fopen(file_name, "w");
if (fp == NULL) {
  /* Handle error */
}

/* ... Process file ... */

if (fclose(fp) != 0) {
  /* Handle error */
}

if (remove(file_name) != 0) {
  /* Handle error */
}
