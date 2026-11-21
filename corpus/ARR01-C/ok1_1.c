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

void clear(int array[], size_t len) {
  for (size_t i = 0; i < len; i++) {
    array[i] = 0;
  }
}

void dowork(void) {
  int dis[12];

  clear(dis, sizeof(dis) / sizeof(dis[0]));
  /* ... */
}
