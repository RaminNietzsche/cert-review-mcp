// corpus: CON34-C noncompliant
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

#include <omp.h>
#include <stdio.h>
 
int main(void) {
  int j = 0;
  #pragma omp parallel
  {
    int t = omp_get_thread_num();
    printf("Running thread - %d\n", t);
    for (int i = 0; i < 5050; i++) {
    j++; /* j not private; could be a race condition */
    }
    printf("Just ran thread - %d\n", t);
    printf("loop count %d\n", j);
  }
return 0;
}
