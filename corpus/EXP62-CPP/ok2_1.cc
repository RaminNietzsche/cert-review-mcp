// corpus: EXP62-CPP compliant
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

struct S {
  int i, j, k;
 
  // ...

  virtual void f();
  void clear() { i = j = k = 0; }
};

void f() {
  S *s = new S;
  // ...
  s->clear();
  // ...
  s->f(); // ok
}
