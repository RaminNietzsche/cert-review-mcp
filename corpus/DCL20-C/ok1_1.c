// corpus: DCL20-C compliant
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

/* In foo.h */
void foo(void);

/* In foo.c */
void foo(void) {
  int i = 3;
  printf("i value: %d\n", i);
}

/* In caller.c */
#include "foo.h"

foo(3);
