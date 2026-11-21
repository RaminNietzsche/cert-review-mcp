// corpus: MEM51-CPP compliant
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
 
struct S {
  static void *operator new(std::size_t size) noexcept(true) {
    return std::malloc(size);
  }
  
  static void operator delete(void *ptr) noexcept(true) {
    std::free(ptr);
  }
};

void f() {
  S *s = new S;
  delete s;
}
