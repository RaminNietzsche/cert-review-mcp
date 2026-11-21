// corpus: CON34-C compliant
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

#include <threads.h>
#include <stdio.h>
#include <stdlib.h>

int child_thread(void *val) {
  int *result = (int *)val;
  printf("Result: %d\n", *result); /* Correctly prints 1 */
  return 0;
}
 
void create_thread(thrd_t *tid, int *value) {
  *value = 1;
  if (thrd_success != thrd_create(tid, child_thread,
                                  value)) {
    /* Handle error */
  }
}
 
int main(void) {
  thrd_t tid;
  int *value = (int *)malloc(sizeof(int));
  if (!value) {
    /* Handle error */
  }
  create_thread(&tid, value);
  if (thrd_success != thrd_join(tid, NULL)) {
    /* Handle error */
  }
  free(value);
  return 0;
}
