// corpus: INT10-C noncompliant
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

int insert(int index, int *list, int size, int value) {
  if (size != 0) {
    index = abs((index + 1) % size);
    list[index] = value;
    return index;
  }
  else {
    return -1;
  }
}
