// corpus: PRE07-C compliant
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

size_t i = /* Some initial value */;
/* Assignment of i */
if (i > 9000) {
   if (puts("Over 9000!?""?!") == EOF) {
     /* Handle error */
   }
}
