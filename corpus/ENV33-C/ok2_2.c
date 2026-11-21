// corpus: ENV33-C compliant
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
#include <ShlObj.h>
#include <Shlwapi.h>
 
#if defined(_MSC_VER)
  #pragma comment(lib, "Shlwapi")
#endif

void func(void) {
  HRESULT hr;
  LPWSTR path = 0;
  WCHAR full_path[MAX_PATH];

  hr = SHGetKnownFolderPath(&FOLDERID_Documents, 0, NULL, &path);
  if (FAILED(hr)) {
    /* Handle error */
  }
  if (!PathCombineW(full_path, path, L".config")) {
    /* Handle error */
  }
  CoTaskMemFree(path);
  if (!DeleteFileW(full_path)) {
    /* Handle error */
  }
}
