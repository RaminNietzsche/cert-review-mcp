// corpus: POS01-C compliant
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

char *file_name = /* some value */;

struct stat orig_st;
if (lstat( file_name, &orig_st) != 0) {
  /* handle error */
}

if (!S_ISREG( orig_st.st_mode)) {
  /* file is irregular or symlink */
}

int fd = open(file_name, O_RDWR);
if (fd == -1) {
  /* handle error */
}

struct stat new_st;
if (fstat(fd, &new_st) != 0) {
  /* handle error */
}

if (orig_st.st_dev != new_st.st_dev ||
    orig_st.st_ino != new_st.st_ino) {
  /* file was tampered with during race window */
}

/* ... file is good, operate on fd ... */
