// corpus: DCL42-C noncompliant
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

int to_add = 2;

int add_some(int x) [[unsequenced]] {
    return x + to_add;
}

int main(void) {
    add_some(-1);
    to_add = 1;
    return add_some(-1);
}
