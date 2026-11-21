// corpus: EXP34-C compliant
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

static unsigned int tun_chr_poll(struct file *file, poll_table *wait)  {
  assert(file);
  struct tun_file *tfile = file->private_data;
  struct tun_struct *tun = __tun_get(tfile);
  struct sock *sk;
  unsigned int mask = 0;

  if (!tun)
    return POLLERR;
  assert(tun->dev);
  sk = tun->sk;
  assert(sk);
  assert(sk->socket);
  /* The remaining code is omitted because it is unchanged... */
}
