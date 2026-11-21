// corpus: INT04-C noncompliant
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

const char *table[] = { "black", "white", "blue", "green" };
 
const char *set_background_color(void) {
  int color_index;
  GET_TAINTED_INTEGER(int, color_index);
 
  const char *color = table[color_index];  /* Violation */
 
  /* ... */
  return color;
} 
