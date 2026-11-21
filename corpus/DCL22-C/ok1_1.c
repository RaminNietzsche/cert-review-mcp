// corpus: DCL22-C compliant
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

#include <stddef.h>
#include <stdint.h>

extern void get_register_bank(volatile int32_t **bank,
                              size_t *num_registers);
extern void external_wait(void);

void func(void) {
  volatile int32_t bank[3];
  size_t num_regs = 3;

  get_register_bank((volatile int32_t **)&bank, &num_regs);
  if (num_regs < 3) {
    /* Handle error */
   }

  bank[0] = 1;
  external_wait();
  bank[0] = 0;
}
