// corpus: PRE00-C compliant
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

int operations = 0, calls_to_F = 0, calls_to_G = 0;
 
inline int f(int x) {
  ++operations;
  ++calls_to_F;
  return 2 * x;
}

inline int g(int x) {
  ++operations;
  ++calls_to_G;
  return x + 1;
}

 
void func(int x) {
  int y = f(x) + g(x);

}
