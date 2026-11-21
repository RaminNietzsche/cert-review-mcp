// corpus: FIO02-C noncompliant
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

/* Verify argv[1] is supplied */

if (!verify_file(argv[1])) {
  /* Handle error */
}

if (fopen(argv[1], "w") == NULL) {
  /* Handle error */
}

/* ... */
