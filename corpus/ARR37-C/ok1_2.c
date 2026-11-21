// corpus: ARR37-C compliant
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

struct numbers {
  short a[3];
};

int sum_numbers(const short *numb, size_t dim) {
  int total = 0;
  for (size_t i = 0; i < dim; ++i) {
    total += numb[i];
  }

  return total;
}

int main(void) {
  struct numbers my_numbers = { .a[0]= 1, .a[1]= 2, .a[2]= 3};
  sum_numbers(
    my_numbers.a,
    sizeof(my_numbers.a)/sizeof(my_numbers.a[0])
  );
  return 0;
}
