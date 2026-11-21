// corpus: WIN04-C compliant
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

#include <Windows.h>
 
void *log_fn = EncodePointer(printf);
/* ... */
int (*fn)(const char *, ...) = (int (*)(const char *, ...))DecodePointer(log_fn);

fn("foo");
