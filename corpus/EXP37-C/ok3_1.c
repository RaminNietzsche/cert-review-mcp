// corpus: EXP37-C compliant
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

/* In another source file */
 
long f(long x) {
  return x < 0 ? -x : x;
}

/* f prototype in scope in this source file */

long f(long x); 

long g(int x) {
  return f((long)x);  
}
