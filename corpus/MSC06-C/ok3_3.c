// corpus: MSC06-C compliant
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

/* my_memset_s.c */
int my_memset_s(void *v, int c, size_t n) {
  if (v == NULL) return EINVAL;

  volatile unsigned char *p = v;
  while (n--) {
    *p++ = c;
  }

  return 0;
}

/* getPassword.c */

extern int my_memset_s(void *v, int c, size_t n);

void getPassword(void) {
  char pwd[64];

  if (retrievePassword(pwd, sizeof(pwd))) {
     /* Checking of password, secure operations, etc. */
  }
  if (my_memset_s(pwd, 0, sizeof(pwd)) != 0) {
    /* Handle error */
  }
}
