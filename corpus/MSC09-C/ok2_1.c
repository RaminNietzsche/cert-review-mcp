// corpus: MSC09-C compliant
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

char myFilename[1000];
const char elimNewln[] = "\n";
const char badChars[] = "-\n\r ,;'\\<\"";
do {
  fgets(myFilename, sizeof(myFilename)-1, stdin);
  myFilename[sizeof(myFilename)-1] ='\0';
  myFilename[strcspn(myFilename, elimNewln)]='\0';
} while ( (strcspn(myFilename, badChars))
           < (strlen(myFilename)));
