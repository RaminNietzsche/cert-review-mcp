// corpus: WIN02-C noncompliant
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
 
void launch_notepad(void) {
  PROCESS_INFORMATION pi;
  STARTUPINFO si;
 
  ZeroMemory(&si, sizeof(si));
  si.cb = sizeof( si );
  if (CreateProcess(TEXT("C:\\Windows\\Notepad.exe"), NULL, NULL, NULL, TRUE,
                    0, NULL, NULL, &si, &pi )) {
    /* Process has been created; work with the process and wait for it to
       terminate. */
    WaitForSingleObject(pi.hProcess, INFINITE);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
  }
}
