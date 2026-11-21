// corpus: ENV34-C compliant
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
#include <threads.h>
#include <time.h>

char now[1024];

int how_soon_is_now(void *) {
  time_t n1;
  if ((time_t) -1 == time(&n1)) {
    // Handle Error
  }
  if (strftime(now, sizeof now, "%Y-%m-%d %H:%M:%S %Z",
               localtime(&n1)) <=  0) {
    // Handle Error
  }
  return 0;
}

int main(void) {
  thrd_t thr;
  if (thrd_success != thrd_create(&thr, how_soon_is_now, 0)) {
    // Handle Error
  }

  int retval;
  if (thrd_success != thrd_join(thr, &retval)) {
    // Handle Error
  }

  puts("The time is: ");
  puts(now);
  return 0;
}
