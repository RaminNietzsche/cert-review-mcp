// corpus: DCL60-CPP noncompliant
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

// s.h
struct S {
  char c;
  int a;
};
 
void init_s(S &s);
 
// s.cpp
#include "s.h"
 
void init_s(S &s) {
  s.c = 'a';
  s.a = 12;
}
 
// a.cpp
#pragma pack(push, 1)
#include "s.h"
#pragma pack(pop)
 
void f() {
  S s;
  init_s(s);
}
