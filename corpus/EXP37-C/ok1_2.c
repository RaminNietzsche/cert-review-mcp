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

#include <tgmath.h>
 
void func(void) {
  double complex c = 2.0 + 4.0 * I;
  double complex result = log2(creal(c));
}
