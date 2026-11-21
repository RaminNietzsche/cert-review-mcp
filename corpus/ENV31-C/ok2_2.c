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

#if defined (_POSIX_) || defined (__USE_POSIX)
  extern char **environ;
  #define envp environ
#elif defined(_WIN32)
  _CRTIMP extern char **_environ;
  #define envp _environ
#endif

int main(int argc, char *argv[]) {
  /* ... */
}
