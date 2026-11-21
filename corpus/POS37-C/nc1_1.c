// corpus: POS37-C noncompliant
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

/* Code intended to run with elevated privileges */

/* Temporarily drop privileges */
if (seteuid(getuid()) != 0) {
  /* Handle error */
}

/* Code intended to run with lower privileges */

if (need_more_privileges) {
  /* Restore privileges */
  if (seteuid(0) != 0) {
    /* Handle error */
  }

  /* Code intended to run with elevated privileges */
}

/* ... */

/* Permanently drop privileges */
if (setuid(getuid()) != 0) {
  /* Handle error */
}

/*
 * Code intended to run with lower privileges,
 * but if privilege relinquishment failed,
 * attacker can regain elevated privileges!
 */
