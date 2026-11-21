// corpus: EXP36-C noncompliant
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

#include <string.h>
 
struct foo_header {
  int len;
  /* ... */
};
 
void func(char *data, size_t offset) {
  struct foo_header *tmp;
  struct foo_header header;

  tmp = (struct foo_header *)(data + offset);
  memcpy(&header, tmp, sizeof(header));

  /* ... */
}
