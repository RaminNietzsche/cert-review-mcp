// corpus: FIO22-C compliant
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

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
 
extern const char *get_validated_editor(void);
 
void func(const char *file_name) {
  int flags;
  const char *editor;

  int fd = open(file_name, O_RDONLY);
  if (fd == -1) {
    /* Handle error */
  }

  flags = fcntl(fd, F_GETFD);
  if (flags == -1) {
    /* Handle error */
  }

  if (fcntl(fd, F_SETFD, flags | FD_CLOEXEC) == -1) {
    /* Handle error */
  }

  editor = get_validated_editor();
  if (editor == NULL) {
    /* Handle getenv() error */
  }
 
  if (system(editor) == -1) {
    /* Handle error */
  }
}
