// corpus: FIO44-C compliant
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

#include <stdio.h>
#include <string.h>
 
int opener(FILE *file) {
  int rc;
  fpos_t offset;

  if (file == NULL) {
    return -1;
  }

  rc = fgetpos(file, &offset);
  if (rc != 0 ) {
    return rc;
  }

  /* Read in data from file */

  rc = fsetpos(file, &offset);
  if (rc != 0 ) {
    return rc;
  }

  return 0;
}
