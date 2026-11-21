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

void func(TCHAR *input) {
  STARTUPINFO si = { 0 };
  PROCESS_INFORMATION pi;
  si.cb = sizeof(si);
  if (!CreateProcess(TEXT("any_cmd.exe"), input, NULL, NULL, FALSE,
                     0, 0, 0, &si, &pi)) {
    /* Handle error */
  }
  CloseHandle(pi.hThread);
  CloseHandle(pi.hProcess);
}
