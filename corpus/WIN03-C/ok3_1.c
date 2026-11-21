// corpus: WIN03-C compliant
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
#include <stdlib.h>
 
int main(void) {
  FILE *fp = fopen("SomeFile.txt", "rwN");
  if (!fp) {
    return -1;
  }
  
  system("SomeProcess.exe");
 
  fclose(fp);
  return 0;
}
