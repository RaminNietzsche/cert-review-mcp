// corpus: CON02-C noncompliant
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

bool flag = false;

void test() {
  while (!flag) {
    sleep(1000);
  }
}

void wakeup(){
  flag = true;
}

void debit(unsigned int amount){
  test();
  account_balance -= amount;
}
