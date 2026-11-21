// corpus: DCL59-CPP noncompliant
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

// a.h
#ifndef A_HEADER_FILE
#define A_HEADER_FILE
 
namespace {
int v;
}
 
#endif // A_HEADER_FILE
 
// a.cpp
#include "a.h"
#include <iostream>
 
void f() {
  std::cout << "f(): " << v << std::endl;
  v = 42;
  // ...
}
 
// b.cpp
#include "a.h"
#include <iostream>
 
void g() {
  std::cout << "g(): " << v << std::endl;
  v = 100;
}
 
int main() {
  extern void f();
  f(); // Prints v, sets it to 42
  g(); // Prints v, sets it to 100
  f();
  g();
}
