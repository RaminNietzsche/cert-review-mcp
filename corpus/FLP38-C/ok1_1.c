// corpus: FLP38-C compliant
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

double d = 3.0;
_Decimal64 d64 = 2.0;
double result = remainder((double) d64, d);
printf("result is %lf\n", result);
