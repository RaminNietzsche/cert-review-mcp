// corpus: FLP06-C compliant
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
  short a = 533;
  int b = 6789;
  long c = 466438237;

  float d = a / 7.0f; /* d is 76.14286 */
  double e = b / 30.; /* e is 226.3 */
  double f = (double)c * 789; /* f is 368019768993.0 */
}
