// corpus: POS54-C compliant
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
#include <string.h>
 
int main(int argc, char *argv[]) {
  FILE *out;
  FILE *in;
  size_t size;
  char *ptr;
 
  if (argc != 2) {
    /* Handle error */
  }
 
  in = fmemopen(argv[1], strlen(argv[1]), "r");

  if (in == NULL){
    /* Handle error */
  }
  /* Use in */
 
  out = open_memstream(&ptr, &size);

  if (out == NULL){
    /* Handle error */
  }
  /* Use out */
  return 0;
}
