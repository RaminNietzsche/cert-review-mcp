// corpus: MSC32-C compliant
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

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
 
void func(void) {
  struct timespec ts;
  if (timespec_get(&ts, TIME_UTC) == 0) {
    /* Handle error */
  } else {
    srandom(ts.tv_nsec ^ ts.tv_sec);
    for (unsigned int i = 0; i < 10; ++i) {
      /* Generates different sequences at different runs */
      printf("%ld, ", random());
    }
  }
}
