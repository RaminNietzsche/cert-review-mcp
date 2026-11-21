// corpus: CON07-C noncompliant
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

#include <stdatomic.h>

static atomic_int a;
static atomic_int b;

void init_ab(void) {
  atomic_init(&a, 0);
  atomic_init(&b, 0);
}

int get_sum(void) {
  return atomic_load(&a) + atomic_load(&b);
}
 
void set_values(int new_a, int new_b) {
  atomic_store(&a, new_a);
  atomic_store(&b, new_b);
}
