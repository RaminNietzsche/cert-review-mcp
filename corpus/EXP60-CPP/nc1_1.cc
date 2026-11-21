// corpus: EXP60-CPP noncompliant
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

// library.h
struct S {
  virtual void f() { /* ... */ }
};
 
void func(S &s); // Implemented by the library, calls S::f()
 
// application.cpp
#include "library.h"
 
void g() {
  S s;
  func(s);
}
