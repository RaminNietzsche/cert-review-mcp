// corpus: SIG01-C compliant
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

/* 
 * Equivalent to signal(SIGUSR1, handler) but makes
 * signal nonpersistent.
 */
struct sigaction act;
act.sa_handler = handler;
act.sa_flags = SA_RESETHAND;
if (sigemptyset(&act.sa_mask) != 0) {
  /* Handle error */
}
if (sigaction(SIGUSR1, &act, NULL) != 0) {
  /* Handle error */
}
