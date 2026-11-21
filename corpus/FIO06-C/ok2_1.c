// corpus: FIO06-C compliant
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
int file_access_permissions;

/* Initialize file_name and file_access_permissions */

int fd = open(
  file_name,
  O_CREAT | O_WRONLY,
  file_access_permissions
);
if (fd == -1){
  /* Handle error */
}
