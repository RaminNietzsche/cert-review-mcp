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

  if ((fin1 = fopen("some_file", "r")) != NULL) {
    if ((fin2 = fopen("some_other_file", "r")) != NULL) {
      if ((obj = malloc(sizeof(object_t))) != NULL) {

        /* ... More code ... */

        /* Clean-up & handle errors */
        free(obj);
      } else {
        ret_val = errno;
      }
      fclose(fin2);
    } else {
      ret_val = errno;
    }
    fclose(fin1);
  } else {
    ret_val = errno;
  }

  return ret_val;
}
