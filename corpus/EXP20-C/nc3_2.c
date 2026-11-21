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

int check_password(User *user, char *pw_given) {
  if (!strcmp((user->password),pw_given)) {
    return 1;
  }
  return 0;

}

void login(char *usr, char *pw) {
  User user = find_user(usr);
  if (!check_password(user, pw)) {
    grantAccess();
  }
  else {
    denyAccess("Incorrect Password");
  }
}
