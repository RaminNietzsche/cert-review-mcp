// corpus: ERR59-CPP compliant
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

// library.h
int func() noexcept(true); // Implemented by the library

// library.cpp
int func() noexcept(true) {
  // ...
  if (/* ... */) {
    return 42;
  }
  // ...
  return 0;
}
 
// application.cpp
#include "library.h"

void f() {
  if (int err = func()) {
    // Handle error
  }
}
