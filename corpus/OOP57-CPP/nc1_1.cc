// corpus: OOP57-CPP noncompliant
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

#include <cstring>
#include <iostream>
 
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
 
void f() {
  C c;
  
  // ... Code that mutates c ... 
  
  // Reinitialize c to its default state
  std::memset(&c, 0, sizeof(C));
  
  std::cout << c.f(100) << std::endl;
}
