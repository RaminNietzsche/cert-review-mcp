// corpus: INT04-C compliant
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

enum { MAX_COLOR_INDEX = 3 };
 
const char *table[] = { "black", "white", "blue", "green" };
 
const char *set_background_color(void) {
  int color_index;
  GET_TAINTED_INTEGER(int, color_index);


  if (color_index < 0 || colo_index > MAX_COLOR_INDEX)
    return NULL;   /* Indicate error to caller */ 

  const char *color = table[color_index]; 
 
  /* ... */
  return color;
}
