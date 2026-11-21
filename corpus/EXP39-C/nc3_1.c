// corpus: EXP39-C noncompliant
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

#include <stdlib.h>
 
struct gadget {
  int i;
  double d;
  char *p;
};
 
struct widget {
  char *q;
  int j;
  double e;
};
 
void func(void) {
  struct gadget *gp;
  struct widget *wp;
 
  gp = (struct gadget *)malloc(sizeof(struct gadget));
  if (!gp) {
    /* Handle error */
  }
  /* ... Initialize gadget ... */
  wp = (struct widget *)realloc(gp, sizeof(struct widget));
  if (!wp) {
    free(gp);
    /* Handle error */
  }
  if (wp->j == 12) {
    /* ... */
  }
  /* ... */
  free(wp);
}
