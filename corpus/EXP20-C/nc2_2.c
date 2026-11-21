// corpus: EXP20-C noncompliant
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

errno_t validateUser(User usr) {
  if(list_contains(allUsers, usr) == 0) {
    return 303; /* User not found error code */
  }
  if(list_contains(validUsers, usr) == 0) {
    return 304; /* Invalid user error code */
  }

  return 0;
}

void processRequest(User usr, Request request) {
  if(!validateUser(usr)) {
    return "invalid user";
  }
  else {
    serveResults();
  }
}
