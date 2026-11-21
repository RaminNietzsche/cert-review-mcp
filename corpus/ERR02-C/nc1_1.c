// corpus: ERR02-C noncompliant
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
ssize_t count = 0;

for (i = 0; i < 9; ++i) {
  count += sprintf(
    buf + count, "%02x ", ((u8 *)&slreg_num)[i]
  );
}
count += sprintf(buf + count, "\n");
