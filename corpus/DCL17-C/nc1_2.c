// corpus: DCL17-C noncompliant
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

foo:
  movl $0, y
  movl x, %eax
  jmp .L2
.L3:
  movl y, %eax
  incl %eax
  movl %eax, y
.L2:
  movl y, %eax
  cmpl $10, %eax
  jg .L3
  ret
