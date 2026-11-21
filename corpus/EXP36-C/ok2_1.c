// corpus: EXP36-C compliant
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

int *loop_function(int *v_pointer) {
  /* ... */
  return v_pointer;
}
 
void func(int *loop_ptr) {
  int *int_ptr = loop_function(loop_ptr);

  /* ... */
}
