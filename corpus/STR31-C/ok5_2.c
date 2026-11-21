// corpus: STR31-C compliant
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

#define __STDC_WANT_LIB_EXT1__ 1
#include <stdlib.h>
#include <string.h>
 
int main(int argc, char *argv[]) {
  /* Ensure argv[0] is not null */
  const char *const name = (argc && argv[0]) ? argv[0] : "";
  char *prog_name;
  size_t prog_size;

  prog_size = strlen(name) + 1;
  prog_name = (char *)malloc(prog_size);

  if (prog_name != NULL) {
    if (strcpy_s(prog_name, prog_size, name)) {
      /* Handle  error */
    }
  } else {
    /* Handle error */
  }
  /* ... */
  free(prog_name);
  return 0;
}
