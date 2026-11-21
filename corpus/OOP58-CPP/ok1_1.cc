// corpus: OOP58-CPP compliant
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

#include <algorithm>
#include <vector>

class A {
  int m;
  
public:
  A() : m(0) {}
  explicit A(int m) : m(m) {}
  
  A(const A &other) : m(other.m) {}
  A(A &&other) : m(other.m) { other.m = 0; }
  
  A& operator=(const A &other) {
    if (&other != this) {
      m = other.m;
    }
    return *this;
  }
 
  A& operator=(A &&other) {
    m = other.m;
    other.m = 0;
    return *this;
  }
  
  int get_m() const { return m; }
};

void f() {
  std::vector<A> v{10};
  A obj(12);
  std::fill(v.begin(), v.end(), obj);
}
