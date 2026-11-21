// corpus: ERR30-C noncompliant
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

#include <errno.h>
#include <limits.h>
#include <stdlib.h>
 
void func(const char *c_str) {
  unsigned long number;
  char *endptr;
  
  number = strtoul(c_str, &endptr, 0);
  if (endptr == c_str || (number == ULONG_MAX 
                         && errno == ERANGE)) {
    /* Handle error */
  } else {
    /* Computation succeeded */
  }
}
