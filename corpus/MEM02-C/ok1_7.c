// corpus: MEM02-C compliant
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

enum month { Jan, Feb, /* ... */ };
typedef enum month month;

typedef struct date date;
struct date {
  unsigned char dd;
  month mm;
  unsigned yy;
};

typedef struct string string;
struct string {
  size_t length;
  char text[];
};

date *d, *week, *fortnight;
string *name;

d = MALLOC(date);
week = MALLOC_ARRAY(7, date);
name = MALLOC_FLEX(string, 16, char);
fortnight = CALLOC(14, date);
