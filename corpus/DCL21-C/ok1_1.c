// corpus: DCL21-C compliant
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

#include <stdio.h>

typedef struct int_struct {
  int x;
} int_struct;

#define MAX_INTS 10

int main(void){
  size_t i;
  int_struct ints[MAX_INTS];

  for (i = 0; i < MAX_INTS; i++) {
    ints[i] = (int_struct){i};
  }

  for (i = 0; i < MAX_INTS; i++) {
    printf("%d\n", ints[i].x);
  }
 
  return 0;
}
