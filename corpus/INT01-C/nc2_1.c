// corpus: INT01-C noncompliant
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

void *alloc(unsigned int blocksize) {
  return malloc(blocksize);
}

int read_counted_string(int fd) {
  unsigned long length;
  unsigned char *data;

  if (read_integer_from_network(fd, &length)) {
    return -1;
  }

  data = (unsigned char*)alloc(length+1);
  if (data == NULL) {
    return -1;  /* Indicate failure */
  }

  if (read_network_data(fd, data, length)) {
    free(data);
    return -1;
  }
  data[length] = '\0';

  /* ... */
  free( data);
  return 0;
}
