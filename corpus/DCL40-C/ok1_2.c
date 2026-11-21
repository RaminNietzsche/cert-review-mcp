// corpus: DCL40-C compliant
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

/* In a.c */
extern int a[];   

int f(unsigned int i, int x) {
  int tmp = a[i];   
  a[i] = x;         
  return tmp;
}

/* In b.c */
int a[] = { 1, 2, 3, 4 };  
