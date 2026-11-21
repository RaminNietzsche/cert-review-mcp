// corpus: MEM04-C compliant
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

size_t size;

/* Initialize size, possibly by user-controlled input */

if (size == 0) {
  /* Handle error */
}
int *list = (int *)malloc(size);
if (list == NULL) {
  /* Handle allocation error */
}
/* Continue processing list */
