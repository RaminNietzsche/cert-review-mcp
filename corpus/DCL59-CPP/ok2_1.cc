// corpus: DCL59-CPP compliant
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
 
extern int v;

inline int get_v() {
  return v;
}

#endif // A_HEADER_FILE
 
// a.cpp
#include "a.h"
 
// Externally used by get_v();
int v;
 
void f() {
  int i = get_v();
  // ...
}
 
// b.cpp
#include "a.h"
 
void g() {
  int i = get_v();
  // ...
}
