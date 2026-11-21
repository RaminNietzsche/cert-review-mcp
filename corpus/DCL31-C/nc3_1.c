// corpus: DCL31-C noncompliant
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

#include <limits.h>
#include <stdio.h>
 
foo(void) {
  return UINT_MAX;
}

int main(void) {
  long long int c = foo();
  printf("%lld\n", c);
  return 0;
}
