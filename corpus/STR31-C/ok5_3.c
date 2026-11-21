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

int main(int argc, char *argv[]) {
  /* Ensure argv[0] is not null */
  const char * const prog_name = (argc && argv[0]) ? argv[0] : "";
  /* ... */
  return 0;
}
