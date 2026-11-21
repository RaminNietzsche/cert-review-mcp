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
extern int f(int a);   

int g(int a) {
  return f(a);   
}

/* In b.c */
int f(int a) {   
  return a * 2;
}
