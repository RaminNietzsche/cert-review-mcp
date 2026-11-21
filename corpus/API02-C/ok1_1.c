// corpus: API02-C compliant
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

char *improved_strncpy(char * restrict s1, size_t s1count, const char * restrict s2, size_t s2count, size_t n);
char *improved_strncat(char * restrict s1, size_t s1count, const char * restrict s2, size_t s2count, size_t n);
