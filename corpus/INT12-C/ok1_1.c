// corpus: INT12-C compliant
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

struct {
  unsigned int a: 8;
} bits = {255};

int main(void) {
  printf("bits.a = %d.\n", bits.a);
  return 0;
}
