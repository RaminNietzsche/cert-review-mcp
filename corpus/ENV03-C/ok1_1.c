// corpus: ENV03-C compliant
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

char *pathbuf;
size_t n;

if (clearenv() != 0) {
  /* Handle error */
}

n = confstr(_CS_PATH, NULL, 0);
if (n == 0) {
  /* Handle error */
}

if ((pathbuf = malloc(n)) == NULL) {
  /* Handle error */
}

if (confstr(_CS_PATH, pathbuf, n) == 0) {
  /* Handle error */
}

if (setenv("PATH", pathbuf, 1) == -1) {
  /* Handle error */
}

if (setenv("IFS", " \t\n", 1) == -1) {
  /* Handle error */
}

if (system("ls dir.`date +%Y%m%d`") == -1) {
  /* Handle error */
}
