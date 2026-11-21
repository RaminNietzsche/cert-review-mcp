// corpus: MSC37-C noncompliant
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

#include <string.h>
#include <stdio.h>
 
int checkpass(const char *password) {
  if (strcmp(password, "pass") == 0) {
    return 1;
  }
}

void func(const char *userinput) {
  if (checkpass(userinput)) {
    printf("Success\n");
  }
}
