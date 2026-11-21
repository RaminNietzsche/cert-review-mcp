// corpus: WIN01-C compliant
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
LONG ShouldThreadExit = 0;

/* Thread 1 */
DWORD WINAPI ThreadProc(LPVOID param) {
  while (1) {
    /* Performing work */
    if (1 == InterlockedCompareExchange(&ShouldThreadExit, 0, 1))
      return 0xFF;
  }
}
 
/* Thread 2 */
InterlockedExchange(&ShouldThreadExit, 1);
