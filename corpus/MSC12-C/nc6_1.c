// corpus: MSC12-C noncompliant
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

if (a == b && a == b) { // if the first one is true, the second one is too
  do_x();
}
if (a == c || a == c ) { // if the first one is true, the second one is too
  do_w();
}
