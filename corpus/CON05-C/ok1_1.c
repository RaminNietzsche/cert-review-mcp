// corpus: CON05-C compliant
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

#include <stdio.h>
#include <threads.h>
 
mtx_t mutex;
 
int thread_foo(void *ptr) {
  int result;
  FILE *fp = fopen("SomeNetworkFile", "r");
 
  if (fp != NULL) {
    /* Work with the file */
    fclose(fp);
  }

  if ((result = mtx_lock(&mutex)) != thrd_success) {
    /* Handle error */
  }

  /* ... */

  if ((result = pthread_mutex_unlock(&mutex)) != 0) {
    /* Handle error */
  }

  return 0;
}
