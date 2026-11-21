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
#include <string>

namespace my {
struct string : std::string {
  explicit string(const char *msg,
                  const std::string::allocator_type &alloc = std::string::allocator_type{}) noexcept
  try : std::string(msg, alloc) {} catch(...) {
    extern void log_message(const char *) noexcept;
    log_message("std::string constructor threw an exception");
    std::terminate();
  }
  // ...
};
}
 
static const my::string global("...");

int main() {
  // ...
}
