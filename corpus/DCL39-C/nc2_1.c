// corpus: DCL39-C noncompliant
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

struct test {
  int a;
  char b;
  int c;
};

/* Safely copy bytes to user space */
extern int copy_to_user(void *dest, void *src, size_t size);

void do_stuff(void *usr_buf) {
  struct test arg;

  /* Set all bytes (including padding bytes) to zero */
  memset(&arg, 0, sizeof(arg));

  arg.a = 1;
  arg.b = 2;
  arg.c = 3;

  copy_to_user(usr_buf, &arg, sizeof(arg));
}
