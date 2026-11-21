// corpus: INT16-C compliant
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

unsigned int value;

if (scanf("%u", &value) == 1) {
  if (value & 0x1 != 0) {
    /* Take action if value is odd */
  }
}
