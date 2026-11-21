// corpus: POS35-C noncompliant
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

char *filename = /* file name */;
char *userbuf = /* user data */;
unsigned int userlen = /* length of userbuf string */;

struct stat lstat_info;
int fd;
/* ... */
if (lstat(filename, &lstat_info) == -1) {
  /* Handle error */
}

if (!S_ISLNK(lstat_info.st_mode)) {
   fd = open(filename, O_RDWR);
   if (fd == -1) {
       /* Handle error */
   }
}
if (write(fd, userbuf, userlen) < userlen) {
  /* Handle error */
}
