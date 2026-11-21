// corpus: POS36-C noncompliant
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

/* Drop superuser privileges in incorrect order */

if (setuid(getuid()) == -1) {
  /* handle error condition */
}
if (setgid(getgid()) == -1) {
  /* handle error condition */
}

/* It is still possible to regain group privileges due to
 * incorrect relinquishment order */
