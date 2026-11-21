// corpus: MSC01-C compliant
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

#define ORIGINYEAR 1980
UINT32 days = /* Input parameter */
int year = ORIGINYEAR;
/* ... */

int daysThisYear = (IsLeapYear(year) ? 366 : 365);
while (days > daysThisYear) {
  days -= daysThisYear;
  year += 1;
  daysThisYear = (IsLeapYear(year) ? 366 : 365);
}
