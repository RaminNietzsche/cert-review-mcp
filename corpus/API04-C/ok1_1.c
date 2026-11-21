// corpus: API04-C compliant
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

errno_t retValue; 
string_m dest, source;  

/* ... */

if (retValue = strcpy_m(dest, source)) { 
  fprintf(stderr, "Error %d from strcpy_m.\n", retValue);
} 
