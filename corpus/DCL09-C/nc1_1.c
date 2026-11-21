// corpus: DCL09-C noncompliant
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

#include <errno.h>
#include <stdio.h>
 
enum { NO_FILE_POS_VALUES = 3 };

int opener(
  FILE *file,
  size_t *width,
  size_t *height,
  size_t *data_offset
) {
  size_t file_w;
  size_t file_h;
  size_t file_o;
  fpos_t offset;

  if (file == NULL) { return EINVAL; }
  errno = 0;
  if (fgetpos(file, &offset) != 0) { return errno; }
  if (fscanf(file, "%zu %zu %zu", &file_w, &file_h, &file_o)
        != NO_FILE_POS_VALUES) {
    return -1;
  }

  errno = 0;
  if (fsetpos(file, &offset) != 0) { return errno; }

  if (width != NULL) { *width = file_w; }
  if (height != NULL) { *height = file_h; }
  if (data_offset != NULL) { *data_offset = file_o; }

  return 0;
}
