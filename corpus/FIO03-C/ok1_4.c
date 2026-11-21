// corpus: FIO03-C compliant
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

TCHAR *file_name;
HANDLE hFile = CreateFile(file_name, GENERIC_READ | GENERIC_WRITE, 0, 0, 
                          CREATE_NEW, FILE_ATTRIBUTE_NORMAL, 0);
if (INVALID_HANDLE_VALUE == hFile) {
  DWORD err = GetLastError();
  if (ERROR_FILE_EXISTS == err) {
    /* Handle file exists error */
  } else {
    /* Handle other error */
  }
}
