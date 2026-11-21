// corpus: EXP43-C noncompliant
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

void func(void) {
  int *restrict p1;
  int *restrict q1;

  int *restrict p2 = p1; /* Undefined behavior */ 
  int *restrict q2 = q1; /* Undefined behavior */ 
 }
