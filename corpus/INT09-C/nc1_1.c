// corpus: INT09-C noncompliant
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

enum Color { red=4, orange, yellow, green, blue, indigo=6, violet };

const char* color_name(enum Color col) {
  switch (col) {
  case red: return "red";
  case orange: return "orange";
  case yellow: return "yellow";
  case green: return "green";
  case blue: return "blue";
  case indigo: return "indigo";   /* Error: duplicate label (yellow) */
  case violet: return "violet";   /* Error: duplicate label (green) */
  }
}
