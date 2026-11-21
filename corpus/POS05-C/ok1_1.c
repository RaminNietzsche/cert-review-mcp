// corpus: POS05-C compliant
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

/*
 * Make sure that the chroot/jail directory exists within
 * the current working directory. Also assign appropriate
 * permissions to the directory to restrict access. Close
 * all file system descriptors to outside resources lest
 * they escape the jail.
 */

if (setuid(0) == -1) {
  /* Handle error */
}

if (chroot("chroot/jail") == -1) {
  /* Handle error */
}

if (chdir("/") == -1) {
  /* Handle error */
}

/* Drop privileges permanently */
if (setgid(getgid()) == -1) {
  /* Handle error */
}

if (setuid(getuid()) == -1) {
  /* Handle error */
}

/* Perform unprivileged operations */
enum {array_max = 100};

FILE *fp = fopen(argv[1], "w");
char x[array_max];
strncpy(x, argv[2], array_max);
x[array_max - 1] = '\0';

/* Write operation is safe within jail */
if (fwrite(x, sizeof(x[0]), sizeof(x)/sizeof(x[0]), fp) <
    sizeof(x)/sizeof(x[0])) {
  /* Handle error */
}
