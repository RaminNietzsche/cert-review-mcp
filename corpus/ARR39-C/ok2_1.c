// corpus: ARR39-C compliant
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
#include <stdlib.h>
#include <stddef.h>
 
struct big {
  unsigned long long ull_a;
  unsigned long long ull_b;
  unsigned long long ull_c;
  int si_d;
  int si_e;
};

void func(void) {
  size_t skip = offsetof(struct big, ull_b);
  unsigned char *ptr = (unsigned char *)malloc(
    sizeof(struct big)
  );
  if (ptr == NULL) {
     /* Handle malloc() error */
  }

  memset(ptr + skip, 0, sizeof(struct big) - skip);
  /* ... */
  free(ptr);
  ptr = NULL;
}
