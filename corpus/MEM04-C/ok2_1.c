// corpus: MEM04-C compliant
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

size_t nsize;
/* Initialize nsize */
char *p2;
char *p = (char *)malloc(100);
if (p == NULL) {
  /* Handle error */
}

/* ... */

p2 = NULL;
if (nsize != 0) {
  p2 = (char *)realloc(p, nsize);
}
if (p2 == NULL) {
  free(p);
  p = NULL;
  return NULL;
}
p = p2;
