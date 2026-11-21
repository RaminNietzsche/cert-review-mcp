// corpus: ARR39-C noncompliant
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

#include <wchar.h>
#include <stdio.h>
 
enum { WCHAR_BUF = 128 };
 
void func(void) {
  wchar_t error_msg[WCHAR_BUF];

  wcscpy(error_msg, L"Error: ");
  fgetws(error_msg + wcslen(error_msg) * sizeof(wchar_t), 
         WCHAR_BUF - 7, stdin);
  /* ... */
}
