// corpus: MSC32-C compliant
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

#include <stdio.h>
#include <Windows.h>
#include <Bcrypt.h>
#include <Ntstatus.h>
#include <Wincrypt.h>

void func(void) {
  BCRYPT_ALG_HANDLE hAlgorithm = NULL;
  long rand_buf;
  PUCHAR pbBuffer = (PUCHAR) &rand_buf;
  ULONG cbBuffer = sizeof(rand_buf);
  ULONG dwFlags = BCRYPT_USE_SYSTEM_PREFERRED_RNG;
  NTSTATUS status;
  for (unsigned int i = 0; i < 10; ++i) {
    status = BCryptGenRandom(hAlgorithm, pbBuffer, cbBuffer, dwFlags);
    if (status == STATUS_SUCCESS) {
      printf("%ld, ", rand_buf);
    } else {
      /* Handle Error */
    }
  }
}
