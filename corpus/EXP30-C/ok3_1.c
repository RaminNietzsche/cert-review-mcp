// corpus: EXP30-C compliant
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

extern void c(int i, int j);
int glob;
 
int a(void) {
  return glob + 10;
}
int b(void) {
  glob = 42;
  return glob;
}
 
void func(void) {
  int a_val, b_val;
 
  a_val = a();
  b_val = b();

  c(a_val, b_val);
}
