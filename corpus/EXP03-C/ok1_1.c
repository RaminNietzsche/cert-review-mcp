// corpus: EXP03-C compliant
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

enum { buffer_size = 50 };

struct buffer {
  size_t size;
  char bufferC[buffer_size];
};

/* ... */

void func(const struct buffer *buf) {

  struct buffer *buf_cpy = 
    (struct buffer *)malloc(sizeof(struct buffer));

  if (buf_cpy == NULL) {
    /* Handle malloc() error */
  }

  /* ... */

  memcpy(buf_cpy, buf, sizeof(struct buffer));

  /* ... */

  free(buf_cpy);
}
