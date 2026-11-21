// corpus: PRE00-C noncompliant
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
 
#define F(x) (++operations, ++calls_to_F, 2 * x)
#define G(x) (++operations, ++calls_to_G, x + 1)

void func(int x) {
  int y = F(x) + G(x);

}
