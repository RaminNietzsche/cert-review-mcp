// corpus: EXP54-CPP noncompliant
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

struct B {};
 
struct D1 : virtual B {};
struct D2 : virtual B {};
 
struct S : D1, D2 {};
 
void f(const B *b) {}
 
void g() {
  S *s = new S;
  // Use s
  delete s;
 
  f(s);
}
