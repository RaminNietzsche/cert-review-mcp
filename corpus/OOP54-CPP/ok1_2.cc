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

#include <new>
#include <utility>
 
struct S { S(const S &) noexcept; /* ... */ };
 
class T {
  int n;
  S *s1;
 
public:
  T(const T &rhs) : n(rhs.n), s1(rhs.s1 ? new S(*rhs.s1) : nullptr) {}
  ~T() { delete s1; }

  // ...
 
  void swap(T &rhs) noexcept {
    using std::swap;
    swap(n, rhs.n);
    swap(s1, rhs.s1);
  }
 
  T& operator=(T rhs) noexcept {
    rhs.swap(*this);
    return *this;
  }
};
