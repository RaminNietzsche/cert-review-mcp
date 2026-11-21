// corpus: MSC13-C noncompliant
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

int *p1;
int *p2;
p1 = foo();
p2 = bar();

if (baz()) {
  return p1;
}
else {
  p2 = p1;
}
return p2;
