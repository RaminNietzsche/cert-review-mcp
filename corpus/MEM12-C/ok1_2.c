// corpus: MEM12-C compliant
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

/* ... Assume the same struct used previously ... */

errno_t do_something(void) {
  FILE *fin1, *fin2;
  object_t *obj;
  errno_t ret_val = NOERR; /* Initially assume a successful return value */

  fin1 = fopen("some_file", "r");
  if (fin1 == NULL) {
    ret_val = errno;
    goto FAIL_FIN1;
  }

  fin2 = fopen("some_other_file", "r");
  if (fin2 == NULL) {
    ret_val = errno;
    goto FAIL_FIN2;
  }

  obj = malloc(sizeof(object_t));
  if (obj == NULL) {
    ret_val = errno;
    goto FAIL_OBJ;
  }

  /* ... More code ... */

SUCCESS:     /* Clean up everything */
  free(obj);

FAIL_OBJ:   /* Otherwise, close only the resources we opened */
  fclose(fin2);

FAIL_FIN2:
  fclose(fin1);

FAIL_FIN1:
  return ret_val;
}
