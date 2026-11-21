// corpus: WIN01-C noncompliant
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
 
DWORD ThreadID;  /* Filled in by call to CreateThread */
 
/* Thread 1 */
DWORD WINAPI ThreadProc(LPVOID param) {
  /* Performing work */
}
 
/* Thread 2 */
HANDLE hThread = OpenThread(THREAD_TERMINATE, FALSE, ThreadID);
if (hThread) {
  TerminateThread(hThread, 0xFF);
  CloseHandle(hThread);
}
