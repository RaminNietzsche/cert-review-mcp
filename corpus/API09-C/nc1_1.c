// corpus: API09-C noncompliant
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

ssize_t atomicio(f, fd, _s, n)
  ssize_t (*f) (int, void *, size_t);
  int fd;
  void *_s;
  size_t n;
{
  char *s = _s;
  ssize_t res, pos = 0;

  while (n > pos) {
    res = (f) (fd, s + pos, n - pos);
    switch (res) {
      case -1:
         if (errno == EINTR || errno == EAGAIN)
         continue;
      case 0:
        return (res);
      default:
        pos += res;
     }
   }
   return (pos);
}
