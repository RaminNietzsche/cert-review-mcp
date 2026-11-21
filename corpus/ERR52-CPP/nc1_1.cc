// corpus: ERR52-CPP noncompliant
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

#include <csetjmp>
#include <iostream>

static jmp_buf env;

struct Counter {
  static int instances;
  Counter() { ++instances; }
  ~Counter() { --instances; }
};

int Counter::instances = 0;

void f() {
  Counter c;
  std::cout << "f(): Instances: " << Counter::instances << std::endl;
  std::longjmp(env, 1);
}

int main() {
  std::cout << "Before setjmp(): Instances: " << Counter::instances << std::endl;
  if (setjmp(env) == 0) {
    f();
  } else {
    std::cout << "From longjmp(): Instances: " << Counter::instances << std::endl;
  }
  std::cout << "After longjmp(): Instances: " << Counter::instances << std::endl;
}
