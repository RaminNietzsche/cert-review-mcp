// corpus: INT15-C compliant
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

#include <stdio.h>
#include <inttypes.h>
#include <errno.h> 

mytypedef_t x;
uintmax_t temp;

/* ... */
if (fgets(buff, sizeof(buff), stdin) == NULL) {
  if (puts("EOF or read error\n") == EOF) {
    /* Handle error */
  }
} else {
  /* Check for errors in the conversion */
  errno = 0;
  temp = strtoumax(buff, &end_ptr, 10);
  if (ERANGE == errno) {
    if (puts("number out of range\n") == EOF) {
      /* Handle error */
    } 
  } else if (end_ptr == buff) {
    if (puts("not valid numeric input\n") == EOF) {
      /* Handle error */
    }
  } else if ('\n' != *end_ptr && '\0' != *end_ptr) {
    if (puts("extra characters on input line\n") == EOF) {
      /* Handle error */
    }
  }
  
  /* No conversion errors, attempt to store the converted value into x */
  if (temp > MYTYPEDEF_MAX) {
    /* Handle error */
  } else {
    x = temp;
  }
}
