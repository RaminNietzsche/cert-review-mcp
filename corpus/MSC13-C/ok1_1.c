// corpus: MSC13-C compliant
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

int *p1 = foo();

/* Removable if bar() does not produce any side effects */
(void)bar();

/* Removable if baz() does not produce any side effects */
(void)baz();
return p1;
