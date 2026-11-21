// corpus: ERR58-CPP compliant
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

#include <exception>
 
int f_helper() noexcept {
  try {
    extern int f() noexcept(false);
    return f();
  } catch (...) {
    extern void log_message(const char *) noexcept;
    log_message("f() threw an exception");
    std::terminate();
  }
  // Unreachable.
}
 
int i = f_helper();

int main() {
  // ...
}
