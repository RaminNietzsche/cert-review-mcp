// corpus: EXP55-CPP noncompliant
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

struct S {
  int i;
  
  S(int i) : i(i) {}
};

void g(S &s) {
  std::cout << s.i << std::endl;
}

void f() {
  volatile S s(12);
  g(const_cast<S &>(s));
}
