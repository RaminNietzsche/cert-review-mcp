// corpus: PRE10-C noncompliant
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

/*
 * Swaps two values and requires
 * tmp variable to be defined.
 */
#define SWAP(x, y) \
  tmp = x; \
  x = y; \
  y = tmp
