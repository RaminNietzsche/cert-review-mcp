// corpus: CON40-C noncompliant
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
#include <stdbool.h>
  
static atomic_bool flag = false;
  
void init_flag(void) {
  atomic_init(&flag, false);
}
  
void toggle_flag(void) {
  atomic_store( &flag, !atomic_load(&flag));
}
    
bool get_flag(void) {
  return atomic_load(&flag);
}
