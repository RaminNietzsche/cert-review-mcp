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

int fd;
long file_size;
char *buffer;

_sopen_s(&fd, "foo.bin", _O_RDONLY, _SH_DENYRW, _S_IREAD);
if (fd == -1) {
  /* Handle error */
}

file_size = _filelength(fd);
if (file_size == -1) {
  /* Handle error */
}

buffer = (char*)malloc(file_size);
if (buffer == NULL) {
  /* Handle error */
}

/* ... */ 
