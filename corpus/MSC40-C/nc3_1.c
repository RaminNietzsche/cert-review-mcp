// corpus: MSC40-C noncompliant
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

/* file1.c */

/* Externally linked definition of the function get_random() */
extern unsigned int get_random(void) {
  /* Initialize the seeds */
  static unsigned int m_z = 0xdeadbeef;
  static unsigned int m_w = 0xbaddecaf;

  /* Compute the next pseudorandom value and update the seeds */
  m_z = 36969 * (m_z & 65535) + (m_z >> 16);
  m_w = 18000 * (m_w & 65535) + (m_w >> 16);
  return (m_z << 16) + m_w;
}
