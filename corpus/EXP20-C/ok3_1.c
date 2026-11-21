// corpus: EXP20-C compliant
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

void login(char *usr, char *pw) {
  User user = find_user(usr);
  if (strcmp((user->password),pw) == 0) {
    grantAccess();
  }
  else {
    denyAccess("Incorrect Password");
  }
}
