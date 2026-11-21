// corpus: POS35-C compliant
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

int fd = open(filename, O_RDWR|O_NOFOLLOW);
if (fd == -1) {
  /* Handle error */
}
if (write(fd, userbuf, userlen) < userlen) {
  /* Handle error */
}
