// corpus: STR06-C compliant
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

char *token;
const char *path = getenv("PATH");
/* PATH is something like "/usr/bin:/bin:/usr/sbin:/sbin" */

char *copy = (char *)malloc(strlen(path) + 1);
if (copy == NULL) {
  /* Handle error */
}
strcpy(copy, path);
token = strtok(copy, ":");
puts(token);

while (token = strtok(0, ":")) {
  puts(token);
}

free(copy);
copy = NULL;

printf("PATH: %s\n", path);
/* PATH is still "/usr/bin:/bin:/usr/sbin:/sbin" */
