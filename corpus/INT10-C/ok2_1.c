// corpus: INT10-C compliant
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

int insert(size_t* result, size_t index, int *list, size_t size, int value) {
  if (size != 0 && size != SIZE_MAX) {
    index = (index + 1) % size;
    list[index] = value;
    *result = index;
    return 1;
  }
  else {
    return 0;
  }
}
