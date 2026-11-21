// corpus: SIG02-C noncompliant
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

void dologout(status) {
  if (logged_in) {
    (void) seteuid((uid_t)0);
    logwtmp(ttyline, "", "");
    /* ... */
  }
  _exit(status);
}

static void lostconn(int signo) {
  if (debug)
    syslog(LOG_DEBUG, "lost connection");
  dologout(-1);
}

static void myoob(signo) {
  if (!transflag)
    return;
  /* ... */
  if (strcmp(cp, "ABOR\r\n") == 0) {
    tmpline[0] = '\0';
    reply(426, "Transfer aborted. Data connection closed.");
    reply(226, "Abort successful");
    longjmp(urgcatch, 1);
  }
  /* ... */
}

/* ... */

signal(SIGPIPE, lostconn);
signal(SIGURG, myoob);
