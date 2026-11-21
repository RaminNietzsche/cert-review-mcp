// corpus: ENV02-C noncompliant
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

if (putenv("TEST_ENV=foo") != 0) {
  /* Handle error */
}
if (putenv("Test_ENV=bar") != 0) {
  /* Handle error */
}

const char *temp = getenv("TEST_ENV");

if (temp == NULL) {
  /* Handle error */
}

printf("%s\n", temp);
