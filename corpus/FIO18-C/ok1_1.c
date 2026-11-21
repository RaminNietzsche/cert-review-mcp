// corpus: FIO18-C compliant
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
#include <string.h>
 
char *buffer = NULL;
size_t size1;
size_t size2;
FILE *filedes;

/* Assume size1 is appropriately initialized */

filedes = fopen("out.txt", "w+");
if (filedes == NULL){
  /* Handle error */
}

buffer = (char *)calloc( 1, size1);
if (buffer == NULL) {
  /* Handle error */
}

/*
 * Accept characters in to the buffer.
 * Check for buffer overflow.
 */

size2 = strlen(buffer) + 1;

fwrite(buffer, 1, size2, filedes);

free(buffer);
buffer = NULL;
fclose(filedes);
