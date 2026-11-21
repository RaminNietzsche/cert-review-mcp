// corpus: CON07-C compliant
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
  
static _Atomic struct ab_s {
  int a, b;
} ab;
 
void init_ab(void) {
  struct ab_s new_ab = {0, 0};
  atomic_init(&ab, new_ab);
}
 
int get_sum(void) {
  struct ab_s new_ab = atomic_load(&ab);
  return new_ab.a + new_ab.b;
}
 
void set_values(int new_a, int new_b) {
  struct ab_s new_ab = {new_a, new_b};
  atomic_store(&ab, new_ab);
}
