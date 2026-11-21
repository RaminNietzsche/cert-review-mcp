// corpus: ARR38-C compliant
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

#include <string.h>

void f4() {
  char p[40];
  const char *q = "Too short";
  size_t n = sizeof(p) < strlen(q) + 1 ? sizeof(p) : strlen(q) + 1;
  memcpy(p, q, n);
}
