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

struct stat st;
char *file_name;

/* Initialize file_name */

int fd = open(file_name, O_RDONLY);
if (fd == -1) {
  /* Handle error */
}

if ((fstat(fd, &st) == -1) ||
   (st.st_uid != getuid()) ||
   (st.st_gid != getgid())) {
  /* File does not belong to user */
}

/*... Read from file ...*/

close(fd);
fd = -1;
