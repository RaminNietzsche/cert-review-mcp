// corpus: ENV31-C compliant
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
 
_CRTIMP extern char **_environ;

int main(int argc, const char *argv[]) {
  if (_putenv_s("MY_NEW_VAR", "new_value") != 0) {
    /* Handle error */
  }
  if (_environ != NULL) {
    for (size_t i = 0; _environ[i] != NULL; ++i) {
      puts(_environ[i]);
    }
  }
return 0;
}
