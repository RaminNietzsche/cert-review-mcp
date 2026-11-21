// corpus: EXP43-C compliant
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

int *a;
int *b;

extern int c[];
 
int main(void) {
  c[0] = 17; 
  c[1] = 18;
  a = &c[0]; 
  b = &c[1];
  a = b; /* Defined behavior */
  /* ... */
}
