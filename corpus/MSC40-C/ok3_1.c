// corpus: MSC40-C compliant
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

/* file2.c */

/* Static inline definition of get_random function */
static inline unsigned int get_random(void) {
  /* 
   * Initialize the seeds. 
   * No more constraint violation; the inline function is now 
   * internally linked. 
   */
  static unsigned int m_z = 0xdeadbeef;
  static unsigned int m_w = 0xbaddecaf;

  /* Compute the next pseudorandom value and update the seeds  */
  m_z = 36969 * (m_z & 65535) + (m_z >> 16);
  m_w = 18000 * (m_w & 65535) + (m_w >> 16);
  return (m_z << 16) + m_w;
}

int main(void) {
  /* Generate pseudorandom numbers using get_random()... */
  return 0;
}
