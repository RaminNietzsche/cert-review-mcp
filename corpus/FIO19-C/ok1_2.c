// corpus: FIO19-C compliant
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

off_t file_size;
char *buffer;
struct stat stbuf;
int fd;
 
fd = open("foo.bin", O_RDONLY);
if (fd == -1) {
  /* Handle error */
}
 
if ((fstat(fd, &stbuf) != 0) || (!S_ISREG(stbuf.st_mode))) {
  /* Handle error */
}
 
file_size = stbuf.st_size;
 
buffer = (char*)malloc(file_size);
if (buffer == NULL) {
  /* Handle error */
}

/* ... */ 
