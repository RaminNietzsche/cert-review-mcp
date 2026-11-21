// corpus: DCL37-C compliant
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

void *my_malloc(size_t nbytes) {
  void *ptr;
  /* Allocate storage from own pool and set ptr */
  return ptr;
}

void *my_aligned_alloc(size_t alignment, size_t size) {
  void *ptr;
  /* Allocate storage from own pool, align properly, set ptr */
  return ptr;
}

void *my_calloc(size_t nelems, size_t elsize) {
  void *ptr;
  /* Allocate storage from own pool, zero memory, and set ptr */
  return ptr;
}

void *my_realloc(void *ptr, size_t nbytes) {
  /* Reallocate storage from own pool and set ptr */
  return ptr;
}

void my_free(void *ptr) {
  /* Return storage to own pool */
}
