// corpus: CON51-CPP compliant
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

#include <mutex>

void manipulate_shared_data(std::mutex &pm) {
  pm.lock();
  try {
    // Perform work on shared data.
  } catch (...) {
    pm.unlock();
    throw;
  }
  pm.unlock(); // in case no exceptions occur
}
