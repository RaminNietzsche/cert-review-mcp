// corpus: MEM33-C noncompliant
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
 
struct flex_array_struct {
  size_t num;
  int data[];
};
 
void func(void) {
  struct flex_array_struct flex_struct;
  size_t array_size = 4;

  /* Initialize structure */
  flex_struct.num = array_size;

  for (size_t i = 0; i < array_size; ++i) {
    flex_struct.data[i] = 0;
  }
}
