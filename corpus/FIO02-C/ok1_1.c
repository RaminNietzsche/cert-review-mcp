// corpus: FIO02-C compliant
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

char *realpath_res = NULL;

/* Verify argv[1] is supplied */

realpath_res = realpath(argv[1], NULL);
if (realpath_res == NULL) {
  /* Handle error */
}

if (!verify_file(realpath_res)) {
  /* Handle error */
}

if (fopen(realpath_res, "w") == NULL) {
  /* Handle error */
}

/* ... */

free(realpath_res);
realpath_res = NULL;
