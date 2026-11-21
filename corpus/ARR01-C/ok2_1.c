// corpus: ARR01-C compliant
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

enum {ARR_LEN = 100};

void clear(int a[], size_t len) {
  memset(a, 0, len * sizeof(int));
}

int main(void) {
  int b[ARR_LEN];
  clear(b, ARR_LEN);
  assert(b[ARR_LEN / 2]==0); /* Cannot fail */
  return 0;
}
