// corpus: MSC24-C compliant
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

#define __STDC_WANT_LIB_EXT1__
#include <string.h>
#include <stdio.h>
 
enum { BUFFERSIZE = 256 };

void complain(const char *msg) {
  static const char prefix[] = "Error: ";
  static const char suffix[] = "\n";
  char buf[BUFFERSIZE];

  strcpy_s(buf, BUFFERSIZE, prefix);
  strcat_s(buf, BUFFERSIZE, msg);
  strcat_s(buf, BUFFERSIZE, suffix);
  fputs(buf, stderr);
}
