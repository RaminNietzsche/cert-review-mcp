// corpus: CON36-C noncompliant
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
#include <threads.h>
 
struct node_t {
  void *node;
  struct node_t *next;
};
 
struct node_t list;
static mtx_t lock;
static cnd_t condition;
 
void consume_list_element(void) {
  if (thrd_success != mtx_lock(&lock)) {
    /* Handle error */
  }
 
  if (list.next == NULL) {
    if (thrd_success != cnd_wait(&condition, &lock)) {
      /* Handle error */
    }
  }

  /* Proceed when condition holds */

  if (thrd_success != mtx_unlock(&lock)) {
    /* Handle error */
  }
}
