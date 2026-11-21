// corpus: POS05-C noncompliant
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

enum { array_max = 100 };

/*
 * Program running with elevated privileges where argv[1]
 * and argv[2] are supplied by the user
 */

char x[array_max];
FILE *fp = fopen(argv[1], "w");

strncpy(x, argv[2], array_max);
x[array_max - 1] = '\0';

/*
 * Write operation to an unintended file such as /etc/passwd
 * gets executed
 */
if (fwrite(x, sizeof(x[0]), sizeof(x)/sizeof(x[0]), fp) <
    sizeof(x)/sizeof(x[0])) {
  /* Handle error */
}
