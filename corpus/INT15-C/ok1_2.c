// corpus: INT15-C compliant
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
#include <inttypes.h>

mytypedef_t x;

/* ... */

#ifdef _MSC_VER
  printf("%llu", (uintmax_t) x);
#else
  printf("%ju", (uintmax_t) x);
#endif  
