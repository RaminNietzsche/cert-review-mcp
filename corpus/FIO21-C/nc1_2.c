// corpus: FIO21-C noncompliant
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

#include <stdio.h>
 
void func(void) {
  char file_name[L_tmpnam];
  FILE *fp;

  if (!tmpnam(file_name)) {
    /* Handle error */
  }

  /* A TOCTOU race condition exists here */

  fp = fopen(file_name, "wb+");
  if (fp == NULL) {
     /* Handle error */
  }
}
