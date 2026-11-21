// corpus: ERR30-C compliant
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

#include <errno.h>
#include <stdio.h>
 
void func(const char *filename) {
  FILE *fileptr;

  errno = 0;
  fileptr = fopen(filename, "rb");
  if (fileptr == NULL)  {
    /*
     * An error occurred in fopen(); now it's valid 
     * to examine errno.
     */
    perror(filename);
  }
}
