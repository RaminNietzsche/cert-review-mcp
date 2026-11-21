// corpus: MSC14-C compliant
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

#define _XOPEN_SOURCE 600
#include <string.h>
#include <stdio.h>
#include <errno.h>
void f() {
  char buf[BUFSIZ];
  int result;

  result = strerror_r(errno, buf, sizeof buf);

  if (0 != result) {
    strcpy(buf, "Unknown error");
  }
  fprintf(stderr, "Error: %s\n", buf);
}
