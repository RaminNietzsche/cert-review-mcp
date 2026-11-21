// corpus: ENV30-C compliant
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

#include <stdlib.h>
#include <string.h>
 
void trstr(char *c_str, char orig, char rep) {
  while (*c_str != '\0') {
    if (*c_str == orig) {
      *c_str = rep;
    }
    ++c_str;
  }
}
 
void func(void) {
  const char *env;
  char *copy_of_env;

  env = getenv("TEST_ENV");
  if (env == NULL) {
    /* Handle error */
  }

  copy_of_env = (char *)malloc(strlen(env) + 1);
  if (copy_of_env == NULL) {
    /* Handle error */
  }

  strcpy(copy_of_env, env);
  trstr(copy_of_env,'"', '_');
  /* ... */
  free(copy_of_env);
}
