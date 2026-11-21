// corpus: MSC04-C noncompliant
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

// */          /* Comment, not syntax error */

f = g/**//h;   /* Equivalent to f = g / h; */

//\
i();           /* Part of a two-line comment */

/\
/ j();         /* Part of a two-line comment */


/*//*/ l();    /* Equivalent to l(); */

m = n//**/o
+ p;           /* Equivalent to m = n + p; */

a = b //*divisor:*/c
+d;            /*
                * Interpreted as a = b/c + d; in c90
                * compiler and a = b + d; in c99 compiler.
                */
