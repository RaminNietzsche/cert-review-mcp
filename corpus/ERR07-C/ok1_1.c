// corpus: ERR07-C compliant
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

long sl;
int si;
char *end_ptr;

if (argc > 1) {
  errno = 0;

  sl = strtol(argv[1], &end_ptr, 10);

  if ((sl == LONG_MIN || sl == LONG_MAX)
   && errno != 0)
  {
    perror("strtol error");
  }
  else if (end_ptr == argv[1]) {
    if (puts("error encountered during conversion") == EOF) {
      /* Handle error */
    }
  }
  else if (sl > INT_MAX) {
    printf("%ld too large!\n", sl);
  }
  else if (sl < INT_MIN) {
    printf("%ld too small!\n", sl);
  }
  else if ('\0' != *end_ptr) {
    if (puts("extra characters on input line\n") == EOF) {
      /* Handle error */
    }
  }
  else {
    si = (int)sl;
  }
}
