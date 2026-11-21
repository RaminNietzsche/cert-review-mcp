// corpus: ERR33-C compliant
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
 
int utf8_to_wcs(wchar_t *wcs, size_t n, const char *utf8,
                size_t *size) {
  if (NULL == size) {
    return -1;
  }
  const char *save = setlocale(LC_CTYPE, "en_US.UTF-8");
  if (NULL == save) {
    return -1;
  }

  *size = mbstowcs(wcs, utf8, n);
  if (NULL == setlocale(LC_CTYPE, save)) {
    return -1;
  }
  return 0;
}
