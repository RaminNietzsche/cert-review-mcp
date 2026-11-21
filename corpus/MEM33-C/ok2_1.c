// corpus: MEM33-C compliant
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
 
struct flex_array_struct {
  size_t num;
  int data[];
};
 
void func(struct flex_array_struct *struct_a,
          struct flex_array_struct *struct_b) {
  if (struct_a->num > struct_b->num) {
    /* Insufficient space; handle error */
    return;
  }
  memcpy(struct_b, struct_a,
         sizeof(struct flex_array_struct) + (sizeof(int)
           * struct_a->num));
}
