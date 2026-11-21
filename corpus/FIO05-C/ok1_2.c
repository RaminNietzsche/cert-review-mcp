// corpus: FIO05-C compliant
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

char *file_name;
FILE *fd;

/* Initialize file_name */

fd = fopen(file_name, "w+");
if (fd == NULL) {
  /* Handle error */
}

/*... Write to file ...*/

/* Go to beginning of file */
fseek(fd, 0, SEEK_SET);

/*... Read from file ...*/

fclose(fd);
fd = NULL;
