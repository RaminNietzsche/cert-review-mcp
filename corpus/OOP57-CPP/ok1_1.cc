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

#include <iostream>
#include <utility>
 
class C {
  int scalingFactor;
  int otherData;
 
public:
  C() : scalingFactor(1) {}
  
  void set_other_data(int i);
  int f(int i) {
    return i / scalingFactor;
  }
  // ...
};
 
template <typename T>
T& clear(T &o) {
  using std::swap;
  T empty;
  swap(o, empty);
  return o;
}

void f() {
  C c;
  
  // ... Code that mutates c ... 
  
  // Reinitialize c to its default state
  clear(c);
  
  std::cout << c.f(100) << std::endl;
}
