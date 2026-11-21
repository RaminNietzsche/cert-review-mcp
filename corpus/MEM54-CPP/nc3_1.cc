// corpus: MEM54-CPP noncompliant
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

struct S {
  S ();
  ~S ();
};

void f() {
  const unsigned N = 32;
  alignas(S) unsigned char buffer[sizeof(S) * N];
  S *sp = ::new (buffer) S[N];
 
  // ...
  // Destroy elements of the array.
  for (size_t i = 0; i != N; ++i) {
    sp[i].~S();
  }
}
