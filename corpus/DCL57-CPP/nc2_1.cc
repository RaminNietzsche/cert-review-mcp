// corpus: DCL57-CPP noncompliant
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
#include <stdexcept>
 
class S {
  bool has_error() const;
 
public:
  ~S() noexcept(false) {
    // Normal processing
    if (has_error() && !std::uncaught_exception()) {
      throw std::logic_error("Something bad");
    }
  }
};
