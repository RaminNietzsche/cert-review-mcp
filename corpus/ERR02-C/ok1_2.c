// corpus: ERR02-C compliant
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

int i;
rsize_t count = 0;
errno_t err;

for (i = 0; i < 9; ++i) {
  err = sprintf_m(
    buf + count, "%02x ", &count, ((u8 *)&slreg_num)[i]
  );
  if (err != 0) {
    /* Handle print error */
  }
}
err = sprintf_m(
  buf + count, "%02x ", &count, ((u8 *)&slreg_num)[i]
);
if (err != 0) {
  /* Handle print error */
}
