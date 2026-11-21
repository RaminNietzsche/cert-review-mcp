// corpus: MSC41-C noncompliant
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <new>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

/* Returns nonzero if authenticated */
int authenticate(const char* code);

int main() {
  if (!authenticate("correct code")) {
    printf("Authentication error\n");
    return -1;
  }

  printf("Authentication successful\n");
  // ...Work with system...
  return 0;
}
