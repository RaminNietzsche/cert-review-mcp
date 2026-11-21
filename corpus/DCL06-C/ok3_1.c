// corpus: DCL06-C compliant
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

#ifndef PORTNUMBER     /* Might be passed on compile line */
#  define PORTNUMBER 1234
#endif

#ifndef HOSTNAME       /* Might be passed on compile line */
#  define HOSTNAME "localhost"
#endif

/* ... */

LDAP *ld = ldap_init(HOSTNAME, PORTNUMBER);
if (ld == NULL) {
  perror("ldap_init");
  return(1);
}
