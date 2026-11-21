// corpus: API00-C noncompliant
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

/* Sets some internal state in the library */
extern int setfile(FILE *file);

/* Performs some action using the file passed earlier */
extern int usefile();

static FILE *myFile;

void setfile(FILE *file) {
    myFile = file;
}

void usefile(void) {
    /* Perform some action here */
}
