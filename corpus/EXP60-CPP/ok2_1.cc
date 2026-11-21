// corpus: EXP60-CPP compliant
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

struct B {
  int i, j;
};

struct D : B {
  float f;
};

extern "Fortran" void func(void *);

void foo(D *d) {
  struct {
    int i, j;
    float f;
  } temp;
 
  temp.i = d->i;
  temp.j = d->j;
  temp.f = d->f;

  func(&temp);
}
