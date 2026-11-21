// corpus: ENV03-C compliant
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

extern char **environ;

int clearenv(void) {
  static char *namebuf = NULL;
  static size_t lastlen = 0;

  while (environ != NULL && environ[0] != NULL) {
    size_t len = strcspn(environ[0], "=");
    if (len == 0) {
      /* Handle empty variable name (corrupted environ[]) */
    }
    if (len > lastlen) {
      namebuf = realloc(namebuf, len+1);
      if (namebuf == NULL) {
        /* Handle error */
      }
      lastlen = len;
    }
    memcpy(namebuf, environ[0], len);
    namebuf[len] = '\0';
    if (unsetenv(namebuf) == -1) {
      /* Handle error */
    }
  }
  return 0;
}
