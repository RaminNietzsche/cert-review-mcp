// corpus: FIO23-C noncompliant
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
 
void cleanup(void) {
  /* Do cleanup */

  printf("All cleaned up!\n");
}

int main(void) {
  atexit(cleanup);
  printf("Doing important stuff\n");

  /* Do important stuff */

  if (fclose(stdout) == EOF) {
    /* Handle error */
  }
  return 0;
}
