// corpus: MEM52-CPP compliant
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

#include <cstring>
 
void f(const int *array, std::size_t size) noexcept(false) {
  int *copy = new int[size];
  // If the allocation fails, it will throw an exception which the caller
  // will have to handle.
  std::memcpy(copy, array, size * sizeof(*copy));
  // ...
  delete [] copy;
}
