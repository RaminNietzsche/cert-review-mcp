// corpus: FIO21-C noncompliant
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
 
void func(void) {
  char file_name[] = "tmp-XXXXXX";
  int fd;

  if (!mktemp(file_name)) {
    /* Handle error */
  }

  /* A TOCTOU race condition exists here */

  fd = open(file_name, O_WRONLY | O_CREAT | O_EXCL | O_TRUNC,
            0600);
  if (fd < 0) {
    /* Handle error */
  }
}
