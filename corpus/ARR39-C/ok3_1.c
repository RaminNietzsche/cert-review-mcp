// corpus: ARR39-C compliant
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
const wchar_t ERROR_PREFIX[7] = L"Error: ";

void func(void) {
  const size_t prefix_len = wcslen(ERROR_PREFIX);
  wchar_t error_msg[WCHAR_BUF];

  wcscpy(error_msg, ERROR_PREFIX);
  fgetws(error_msg + prefix_len,
        WCHAR_BUF - prefix_len, stdin);
  /* ... */
}
