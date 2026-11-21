// corpus: ERR57-CPP compliant
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

struct A {/* ... */};
struct B {/* ... */};
 
class C {
  A *a;
  B *b;
protected:
  void init() noexcept(false);
public:
  C() : a(nullptr), b(nullptr) {
    try {
      a = new A();
      b = new B();
      init();
    } catch (...) {
      delete a;
      delete b;
      throw;
    }
  }
};
