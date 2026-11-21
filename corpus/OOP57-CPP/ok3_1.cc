// corpus: OOP57-CPP compliant
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

class C {
  int i;
 
public:
  virtual void f();
  
  bool operator==(const C &rhs) const {
    return rhs.i == i;
  }

  // ...
};
 
void f(C &c1, C &c2) {
  if (c1 == c2) {
    // ...
  }
}
