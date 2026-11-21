// corpus: EXP33-C compliant
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

#include <time.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/time.h>

void func(void) {     
  clock_t cpu_time;
  struct timeval tv;

  cpu_time = clock();
  if (cpu_time == (clock_t)-1) {
    /* Handle error */
  }
  gettimeofday(&tv, NULL);
  srandom(((unsigned int)getpid() << 16) ^ tv.tv_sec ^ tv.tv_usec ^ cpu_time);
}
