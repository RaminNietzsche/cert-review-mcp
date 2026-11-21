// corpus: POS34-C compliant
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

int func(const char *var) {
  const char *env_format = "TEST=%s";
  const size_t len = strlen(var) + strlen(env_format);
  char *env = (char *) malloc(len);
  if (env == NULL) {
    return -1;
  }
  int retval = snprintf(env, len, env_format, var);
  if (retval < 0 || (size_t)retval >= len) {
    /* Handle error */
  }
  if (putenv(env) != 0) {
    free(env);
    return -1;
  }
  return 0;
}
