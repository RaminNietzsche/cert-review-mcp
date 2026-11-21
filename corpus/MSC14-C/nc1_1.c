// corpus: MSC14-C noncompliant
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

signed int si;
signed int si2;
signed int sum;

if (si < 0 || si2 < 0) {
  /* Handle error condition */
}
if (~si < si2) {
  /* Handle error condition */
}
sum = si + si2;
