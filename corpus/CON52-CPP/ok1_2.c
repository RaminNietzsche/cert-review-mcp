// corpus: CON52-CPP compliant
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

struct MultiThreadedFlags {
  unsigned char flag1;
  unsigned char flag2;
};
 
MultiThreadedFlags flags;
 
void thread1() {
  flags.flag1 = 1;
}

void thread2() {
  flags.flag2 = 2;
}
