// corpus: MSC30-C compliant
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
#include <bcrypt.h>
#include <stdio.h>

#pragma comment(lib, "Bcrypt")

void func(void) {
  BCRYPT_ALG_HANDLE Prov;
  int Buffer;
  if (!BCRYPT_SUCCESS(
          BCryptOpenAlgorithmProvider(&Prov, BCRYPT_RNG_ALGORITHM,
                                      NULL, 0))) {
    /* handle error */
  }
  if (!BCRYPT_SUCCESS(BCryptGenRandom(Prov, (PUCHAR) (&Buffer),
                                      sizeof(Buffer), 0))) {
    /* handle error */
  }
  printf("Random number: %d\n", Buffer);
  BCryptCloseAlgorithmProvider(Prov, 0);
}
