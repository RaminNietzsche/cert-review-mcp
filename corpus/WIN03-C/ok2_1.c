// corpus: WIN03-C compliant
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
 
int CALLBACK WinMain(HINSTANCE hInstance, HINSTANCE hPrev, LPSTR cmdLine, int show) {
  HANDLE hUntrusted = (HANDLE)_strtoui64(cmdLine, NULL, 16);
  HANDLE hFile = NULL;
  BY_HANDLE_FILE_INFORMATION info;
 
  if (!DuplicateHandle(GetCurrentProcess(), hUntrusted, GetCurrentProcess(), &hFile,
                       0, FALSE, DUPLICATE_SAME_ACCESS | DUPLICATE_CLOSE_SOURCE)) {
    /* Handle error; possibly not even a valid handle */
  }
  
  if (!GetFileInformationByHandle(hFile, &info)) {
    /* Handle error; likely not a valid file handle */
 
    // Close the file handle since we no longer trust it.
    CloseHandle(hFile);
    hFile = NULL;
  }
  
  /* Continue working with the file */
}
