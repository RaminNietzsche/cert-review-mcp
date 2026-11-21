// corpus: MSC14-C compliant
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

unsigned int si;
unsigned int si2;
unsigned int sum;

if (si < 0 || si2 < 0) {
  /* Handle error condition */
}
if (INT_MAX - si < si2) {
  /* Handle error condition */
}
sum = si + si2;
