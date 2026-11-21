// corpus: POS38-C noncompliant
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

char c;
pid_t pid;

int fd = open(filename, O_RDWR);
if (fd == -1) {
  /* Handle error */
}
read(fd, &c, 1);
printf("root process:%c\n",c);

pid = fork();
if (pid == -1) {
  /* Handle error */
}

if (pid == 0) { /*child*/
  read(fd, &c, 1);
  printf("child:%c\n",c);
}
else { /*parent*/
  read(fd, &c, 1);
  printf("parent:%c\n",c);
}
