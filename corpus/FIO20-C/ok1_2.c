// corpus: FIO20-C compliant
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
#include <stdlib.h>
#include <string.h>

char *get_filled_buffer(void) {
  char temp[32];
  char *ret = NULL;
  size_t full_length = 0;
   
  while (fgets(temp, sizeof(temp), stdin)) {
    size_t len = strlen(temp);
    if (SIZE_MAX - len - 1 < full_length) {
      break;
    }
    char *r_temp = realloc(ret, full_length + len + 1);
    if (r_temp == NULL) {
      break;
    }
    ret = r_temp;
    strcpy(ret + full_length, temp); /* concatenate */
    full_length += len;
   
    if (feof(stdin) || temp[len-1] == '\n') {
      return ret;
    }
  }

  free(ret);
  return NULL;
}
