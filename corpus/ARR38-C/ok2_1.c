// corpus: ARR38-C compliant
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

#include <stdlib.h>
#include <string.h>
 
void f1(size_t nchars) {
  char *p = (char *)malloc(nchars);
  /* ...  */
  const size_t n = nchars;
  /* ...  */
  memset(p, 0, n);
}
