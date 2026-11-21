// corpus: WIN03-C noncompliant
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
 
void func(void) {
  HANDLE hMutex = OpenMutex(MUTEX_ALL_ACCESS, TRUE, TEXT("Global\\CommonMutex"));
  if (!hMutex) {
    /* Handle error */
  }
}
