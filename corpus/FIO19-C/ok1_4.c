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

HANDLE file;
LARGE_INTEGER file_size;
char *buffer;

 
file = CreateFile(TEXT("foo.bin"), GENERIC_READ, 0, NULL, 
                   OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
if (INVALID_FILE_HANDLE == file) {
  /* Handle error */
}
 
if (!GetFileSizeEx(file, &file_size)) {
  /* Handle error */
}
 
/* 
 * Note: 32-bit portability issue with LARGE_INTEGER
 * truncating to a size_t.
 */
buffer = (char*)malloc(file_size);
if (buffer == NULL) {
  /* Handle error */
}

/* ... */ 
