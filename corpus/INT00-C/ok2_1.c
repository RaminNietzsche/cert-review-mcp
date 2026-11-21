// corpus: INT00-C compliant
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

#if UINT_MAX > UINTMAX_MAX/UINT_MAX
#error No safe type is available.
#endif
/* ... */
unsigned int a, b;
uintmax_t c;
/* Initialize a and b */
c = (uintmax_t)a * b; /* Guaranteed to fit, verified above */
