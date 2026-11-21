// corpus: MEM06-C compliant
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

char *secret;

secret = (char *)VirtualAlloc(0, size + 1, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
if (!secret) {
  /* Handle error */
}

if (!VirtualLock(secret, size+1)) {
    /* Handle error */
}

/* Perform operations using secret... */

SecureZeroMemory(secret, size + 1);
VirtualUnlock(secret, size + 1);
VirtualFree(secret, 0, MEM_RELEASE);
secret = NULL;
