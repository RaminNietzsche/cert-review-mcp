// corpus: FIO42-C compliant
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

#include <Windows.h>
 
int func(LPCTSTR filename) {
  HANDLE hFile = CreateFile(filename, GENERIC_READ, 0, NULL,
                            OPEN_EXISTING,
                            FILE_ATTRIBUTE_NORMAL, NULL);
  if (INVALID_HANDLE_VALUE == hFile) {
    return -1;
  } 
  /* ... */ 
  if (!CloseHandle(hFile)) {
    return -1;
  }
 
  return 0;
}
