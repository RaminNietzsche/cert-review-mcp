// corpus: ERR04-C compliant
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
#include <stdio.h>

int write_data(void) {
  const char *filename = "hello.txt";
  FILE *f = fopen(filename, "w");
  if (f == NULL) {
    /* Handle error */
  }
  fprintf(f, "Hello, World\n");
  /* ... */
  exit(EXIT_FAILURE); /* Writes data and closes f */
  /* ... */
  return 0;
}

int main(void) {
  write_data();
  return EXIT_SUCCESS;
}
