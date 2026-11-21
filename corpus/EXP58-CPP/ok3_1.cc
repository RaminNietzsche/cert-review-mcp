// corpus: EXP58-CPP compliant
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
 
extern "C" void f(const char *s, ...) {
  va_list list;
  va_start(list, s);
  std::cout << (s ? s : "") << ", " << va_arg(list, int);
  va_end(list);
}
