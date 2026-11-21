// corpus: FIO41-C noncompliant
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
 
void func(const char *file_name) {
  FILE *fptr = NULL;
  int c = 'a';
 
  while (c <= 'z') {
    if (putc(c++, fptr ? fptr :
         (fptr = fopen(file_name, "w"))) == EOF) {
      /* Handle error */
    }
  }

  if (fclose(fptr) == EOF) {
    /* Handle error */
  }
}
