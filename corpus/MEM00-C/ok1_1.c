// corpus: MEM00-C compliant
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

enum { MIN_SIZE_ALLOWED = 32 };

int verify_size(const char *list, size_t size) {
  if (size < MIN_SIZE_ALLOWED) {
    /* Handle error condition */
    return -1;
  }
  return 0;
}

void process_list(size_t number) {
  char *list = (char *)malloc(number);

  if (list == NULL) {
    /* Handle allocation error */
  }

  if (verify_size(list, number) == -1) {
      free(list);
      return;
  }

  /* Continue processing list */

  free(list);
}
