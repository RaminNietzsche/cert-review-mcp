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

int validateUser(User usr) {
  if(list_contains(validUsers, usr)) {
    return 1;
  }

  return 0;
}

void processRequest(User usr, Request request) {
  if(validateUser(usr) == 0) {
    return "invalid user";
  }
  else {
    serveResults();
  }
}
