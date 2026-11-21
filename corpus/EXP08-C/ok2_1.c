// corpus: EXP08-C compliant
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

struct big {
  unsigned long long ull_1; /* Typically 8 bytes */
  unsigned long long ull_2; /* Typically 8 bytes */
  unsigned long long ull_3; /* Typically 8 bytes */
  int si_4; /* Typically 4 bytes */
  int si_5; /* Typically 4 bytes */
};
/* ... */
 
int f(void) {
  size_t skip = offsetof(struct big, ull_2);
  struct big *s = (struct big *)malloc(sizeof(struct big));
  if (!s) {
    return -1; /* Indicate malloc() failure */
  }

  memset((char *)s + skip, 0, sizeof(struct big) - skip);
/* ... */
  free(s);
  s = NULL;

  return 0;
}
