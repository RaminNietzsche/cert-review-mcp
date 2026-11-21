// corpus: INT35-C compliant
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

#define PRECISION(value)  _Generic(value, \
  unsigned char : 8, \
  unsigned short: 16, \
  unsigned int : 32, \
  unsigned long : 32, \
  unsigned long long : 64, \
  signed char : 7, \
  signed short : 15, \
  signed int : 31, \
  signed long : 31, \
  signed long long : 63)
