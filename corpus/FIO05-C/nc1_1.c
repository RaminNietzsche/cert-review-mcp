// corpus: FIO05-C noncompliant
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

/* Initialize file_name */

FILE *fd = fopen(file_name, "w");
if (fd == NULL) {
  /* Handle error */
}

/*... Write to file ...*/

fclose(fd);
fd = NULL;

/*
 * A race condition here allows for an attacker  
 * to switch out the file for another. 
 */

/* ... */

fd = fopen(file_name, "r");
if (fd == NULL) {
  /* Handle error */
}

/*... Read from file ...*/

fclose(fd);
fd = NULL;
