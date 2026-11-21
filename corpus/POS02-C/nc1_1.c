// corpus: POS02-C noncompliant
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

int establish(void) {
  struct sockaddr_in sa; /* listening socket's address */
  int s; /* listening socket */

  /*  Fill up the structure with address and port number  */

  sa.sin_port = htons(portnum);

  /*  Other system calls like socket()  */

  if (bind(s, (struct sockaddr *)&sa,
        sizeof(struct sockaddr_in)) < 0) {
    /* Perform cleanup */
  }

  /* Return */
}

int main(void) {
  int s = establish();

  /*  Block with accept() until a client connects  */

  switch (fork()) {
    case -1 :  /* Error, clean up and quit */
    case  0 :  /* This is the child, handle the client */
    default :  /* This is the parent, continue blocking */
  }
  return 0;
}
