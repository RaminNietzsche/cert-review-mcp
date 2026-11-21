// corpus: MSC37-C compliant
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

#include <stddef.h>
 
int getlen(const int *input, size_t maxlen, int delim,
           size_t *result) {
  if (result == NULL) {
    return -1;
  }
  for (size_t i = 0; i < maxlen; ++i) {
    if (input[i] == delim) {
      *result = i;
      return 0;
    }
  }
  return -1;
}

void func(int userdata) {
  size_t i;
  int data[] = {1, 1, 1};
  if (getlen(data, sizeof(data), 0, &i) != 0) {
    /* Handle error */
  } else {
    data[i] = userdata;
  }
}
