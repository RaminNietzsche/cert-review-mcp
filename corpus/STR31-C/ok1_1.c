// corpus: STR31-C compliant
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

#include <stddef.h>
 
void copy(size_t n, char src[n], char dest[n]) {
   size_t i;
 
   for (i = 0; src[i] && (i < n - 1); ++i) {
     dest[i] = src[i];
   }
   dest[i] = '\0';
}
