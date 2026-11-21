// corpus: MSC33-C compliant
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

#include <time.h>

enum { maxsize = 26 };
 
void func(struct tm *time) {
  char s[maxsize];
  /* Current time representation for locale */
  const char *format = "%c";

  size_t size = strftime(s, maxsize, format, time);
  if (size == 0) {
    /* Handle error */
  }
}
