// corpus: EXP59-CPP compliant
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

#include <cstddef>

struct D {
  virtual void f() {}
  struct InnerStandardLayout {
    int i;
  } inner;
};

void f() {
  size_t off = offsetof(D::InnerStandardLayout, i);
  // ...
}
