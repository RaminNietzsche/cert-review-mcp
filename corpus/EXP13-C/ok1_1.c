// corpus: EXP13-C compliant
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

if ( (a < b) && (b < c) ) /* Clearer and probably what was intended */
/* ... */
if ( (a == b) && (a == c) ) /* Ditto */
