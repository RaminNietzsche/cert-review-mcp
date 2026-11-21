// corpus: EXP19-C noncompliant
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

int login;

if (invalid_login())
  login = 0;
else
  printf("Login is valid\n");  /* Debugging line added here */
  login = 1;                   /* This line always gets executed
                               /* regardless of a valid login! */
