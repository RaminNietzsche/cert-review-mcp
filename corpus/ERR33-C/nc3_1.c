// corpus: ERR33-C noncompliant
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

#include <stdlib.h>
 
void *p;
void func(size_t new_size) {
  if (new_size == 0) {
    /* Handle error */
  }
  p = realloc(p, new_size);
  if (p == NULL) {
   /* Handle error */
  }
}
