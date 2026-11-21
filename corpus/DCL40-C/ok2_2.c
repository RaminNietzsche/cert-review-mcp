// corpus: DCL40-C compliant
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

/* In bashline.h */
extern char * bash_groupname_completion(const char *, int);   

/* In a.c */
#include "bashline.h"

void f(const char *s, int i) {
  bash_groupname_completion(s, i);  
}

/* In b.c */
int bash_groupname_completion_funct; 
