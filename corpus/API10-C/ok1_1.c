// corpus: API10-C compliant
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

int tls_connect_by_name(const char *host, int port, int option_bitmask);
#define TLS_DEFAULT_OPTIONS 0
#define TLS_DISABLE_HOST_VALIDATION 0x0001  // use rarely, subject to man-in-the-middle attack
#define TLS_ENABLE_V1_0 0x0002
#define TLS_ENABLE_V1_1 0x0004
