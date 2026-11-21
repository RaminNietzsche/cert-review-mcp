// corpus: MEM54-CPP compliant
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

#include <cstddef>
#include <new>

#if defined(__clang__) || defined(__GNUG__)
  const size_t overhead = sizeof(size_t);
#else
  static_assert(false, "you need to determine the size of your implementation's array overhead");
  const size_t overhead = 0; // Declaration prevents additional diagnostics about overhead being undefined; the value used does not matter.
#endif

struct S {
  S();
  ~S();
};

void *operator new[](size_t n, void *p, size_t bufsize) {
  if (n > bufsize) {
    throw std::bad_array_new_length();
  }
  return p;
}

void f() {
  const size_t n = 32;
  alignas(S) unsigned char buffer[sizeof(S) * n + std::max(overhead, alignof(S))];
  S *sp = ::new (buffer, sizeof(buffer)) S[n];
 
  // ...
  // Destroy elements of the array.
  for (size_t i = 0; i != n; ++i) {
    sp[i].~S();
  }
}
