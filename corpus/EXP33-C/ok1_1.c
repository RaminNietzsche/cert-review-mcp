// corpus: EXP33-C compliant
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

void set_flag(int number, int *sign_flag) {
  if (NULL == sign_flag) {
    return;
  }

  /* Account for number being 0 */
  if (number >= 0) { 
    *sign_flag = 1;
  } else {
    *sign_flag = -1;
  }
}

int is_negative(int number) {
  int sign = 0; /* Initialize for defense-in-depth */
  set_flag(number, &sign);
  return sign < 0;
}
