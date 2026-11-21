// corpus: DCL39-C compliant
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

#include <stddef.h>

#pragma pack(push, 1) /* 1 byte */
struct test {
  int a;
  char b;
  int c;
};
#pragma pack(pop)
 
/* Safely copy bytes to user space */
extern int copy_to_user(void *dest, void *src, size_t size);

void do_stuff(void *usr_buf) {
  struct test arg = {1, 2, 3};
  copy_to_user(usr_buf, &arg, sizeof(arg));
}
