// corpus: ERR01-C compliant
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

printf("This\n");
printf("is\n");
printf("a\n");
printf("test.\n");
if (ferror(stdout)) {
  fprintf(stderr, "printf failed\n");
}
