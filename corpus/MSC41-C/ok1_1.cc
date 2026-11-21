// corpus: MSC41-C compliant
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
#define CODE_LEN 50
  char code[CODE_LEN];
  printf("Please enter your authentication code:\n");
  fgets(code, sizeof(code), stdin);
  int flag = authenticate(code);
  memset_explicit(code, 0, sizeof(code));
  if (!flag) {
    printf("Access denied\n");
    return -1;
  }
  printf("Access granted\n");
  // ...Work with system...
  return 0;
}
