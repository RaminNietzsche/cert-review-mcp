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

#include <assert.h>
#include <limits.h>
#include <stddef.h>

struct test {
  unsigned a : 1;
  unsigned padding1 : sizeof(unsigned) * CHAR_BIT - 1;
  unsigned b : 4;
  unsigned padding2 : sizeof(unsigned) * CHAR_BIT - 4;
};
/* Ensure that we have added the correct number of padding bits. */
static_assert(sizeof(struct test) == sizeof(unsigned) * 2,
              "Incorrect number of padding bits for type: unsigned");

/* Safely copy bytes to user space */
extern int copy_to_user(void *dest, void *src, size_t size);

void do_stuff(void *usr_buf) {
  struct test arg = { .a = 1, .padding1 = 0, .b = 10, .padding2 = 0 };
  copy_to_user(usr_buf, &arg, sizeof(arg));
}
