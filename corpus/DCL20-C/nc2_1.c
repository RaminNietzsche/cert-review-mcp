// corpus: DCL20-C noncompliant
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

/* Compile using gcc4.3.3 */
void foo() {
  /* 
   * Use assembly code to retrieve i
   * implicitly from caller
   * and transfer it to a less privileged file.
   */
}

...

/* Caller */
foo(i); /* i is fed from user input */
