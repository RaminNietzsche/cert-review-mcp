// corpus: API04-C noncompliant
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

char *dir, *file, pname[MAXPATHLEN];

/* ... */

if (strlcpy(pname, dir, sizeof(pname)) >= sizeof(pname)) {
  /* Handle source-string-too long error */
}
