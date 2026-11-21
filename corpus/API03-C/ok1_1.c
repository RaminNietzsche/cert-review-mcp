// corpus: API03-C compliant
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

/* Initialization of pthread attribute objects */
int pthread_condattr_init(pthread_condattr_t *);
int pthread_mutexattr_init(pthread_mutexattr_t *);
int pthread_rwlockattr_init(pthread_rwlockattr_t *);
...
/* Initialization of pthread objects using attributes */
int pthread_cond_init(pthread_cond_t * restrict, const pthread_condattr_t * restrict);
int pthread_mutex_init(pthread_mutex_t * restrict, const pthread_mutexattr_t * restrict);
int pthread_rwlock_init(pthread_rwlock_t * restrict, const pthread_rwlockattr_t * restrict);
...
