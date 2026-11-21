// corpus: FIO41-C compliant
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
  int c = 'a'; 
  FILE *fptr = fopen(file_name, "w");
 
  if (fptr == NULL) {
    /* Handle error */
  }

  while (c <= 'z') {
    if (putc(c++, fptr) == EOF) {
      /* Handle error */
    }
  }

  if (fclose(fptr) == EOF) {
    /* Handle error */
  }
}
