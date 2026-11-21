// corpus: OOP54-CPP compliant
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

  T(T &&rhs) { *this = std::move(rhs); }

  // ... everything except operator= ..

  T& operator=(T &&rhs) noexcept {
    using std::swap;
    swap(n, rhs.n);
    swap(s1, rhs.s1);
    return *this;
  }
