// corpus: MSC38-C noncompliant
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

#include <assert.h>
 
typedef void (*handler_type)(int);
 
void execute_handler(handler_type handler, int value) {
  handler(value);
}
 
void func(int e) {
  execute_handler(&(assert), e < 0);
} 
