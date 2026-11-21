// corpus: FLP37-C compliant
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

#include <stdbool.h>
#include <string.h>
 
struct S {
  int i;
  float f;
};
 
bool are_equal(const struct S *s1, const struct S *s2) {
  if (!s1 && !s2)
    return true;
  else if (!s1 || !s2)
    return false;
  return s1->i == s2->i &&
         s1->f == s2->f;
}
