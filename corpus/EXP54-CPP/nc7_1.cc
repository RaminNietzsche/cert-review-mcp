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

#include <algorithm>
#include <cstddef>
#include <memory>
#include <type_traits>
 
class S {
  int i;

public:
  S() : i(0) {}
  S(int i) : i(i) {}
  S(const S&) = default;
  S& operator=(const S&) = default;
};

template <typename Iter>
void f(Iter i, Iter e) {
  static_assert(std::is_same<typename std::iterator_traits<Iter>::value_type, S>::value,
                "Expecting iterators over type S");
  ptrdiff_t count = std::distance(i, e);
  if (!count) {
    return;
  }
  
  // Get some temporary memory.
  auto p = std::get_temporary_buffer<S>(count);
  if (p.second < count) {
    // Handle error; memory wasn't allocated, or insufficient memory was allocated.
    return;
  }
  S *vals = p.first; 
  
  // Copy the values into the memory.
  std::copy(i, e, vals);
  
  // ...
  
  // Return the temporary memory.
  std::return_temporary_buffer(vals);
}
