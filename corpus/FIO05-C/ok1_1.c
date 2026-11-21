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

struct stat orig_st;
struct stat new_st;
char *file_name;

/* Initialize file_name */

int fd = open(file_name, O_WRONLY);
if (fd == -1) {
  /* Handle error */
}

/*... Write to file ...*/

if (fstat(fd, &orig_st) == -1) {
  /* Handle error */
}
close(fd);
fd = -1;

/* ... */

fd = open(file_name, O_RDONLY);
if (fd == -1) {
  /* Handle error */
}

if (fstat(fd, &new_st) == -1) {
  /* Handle error */
}

if ((orig_st.st_dev != new_st.st_dev) ||
    (orig_st.st_ino != new_st.st_ino)) {
  /* File was tampered with! */
}

/*... Read from file ...*/

close(fd);
fd = -1;
