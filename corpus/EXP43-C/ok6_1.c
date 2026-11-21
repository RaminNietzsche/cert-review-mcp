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

void func(void) {
  int *restrict p1;   
  int *restrict q1;
  {  /* Added inner block */
    int *restrict p2 = p1; /* Valid, well-defined behavior */    
    int *restrict q2 = q1; /* Valid, well-defined behavior */ 
  }
}
