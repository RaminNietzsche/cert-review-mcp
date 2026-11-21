// corpus: ENV30-C compliant
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

#include <locale.h>
#include <stdlib.h>
#include <string.h>
 
void f2(void) {
  const struct lconv *conv = localeconv();
  if (conv == NULL) {
     /* Handle error */
  }
  
  struct lconv *copy_of_conv = (struct lconv *)malloc(
    sizeof(struct lconv));
  if (copy_of_conv == NULL) {
    /* Handle error */
  }
 
  memcpy(copy_of_conv, conv, sizeof(struct lconv));
 
  if ('\0' == copy_of_conv->decimal_point[0]) {
    copy_of_conv->decimal_point = ".";  
  }
  /* ... */
  free(copy_of_conv);
}
