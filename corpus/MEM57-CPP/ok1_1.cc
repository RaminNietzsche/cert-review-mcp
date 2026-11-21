// corpus: MEM57-CPP compliant
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

#include <cstdlib>
#include <new>

struct alignas(32) Vector {
  char elems[32];
  static void *operator new(size_t nbytes) {
    if (void *p = std::aligned_alloc(alignof(Vector), nbytes)) {
      return p;
    }
    throw std::bad_alloc();
  }
  static void operator delete(void *p) {
    free(p);
  }
};

Vector *f() {
  Vector *pv = new Vector;
  return pv;
}
