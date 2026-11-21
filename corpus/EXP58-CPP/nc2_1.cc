// corpus: EXP58-CPP noncompliant
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

#include <cstdarg>
#include <iostream>
 
extern "C" void f(int &a, ...) {
  va_list list;
  va_start(list, a);
  if (a) {
    std::cout << a << ", " << va_arg(list, int);
    a = 100; // Assign something to a for the caller
  }
  va_end(list);
}
