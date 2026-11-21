// corpus: CTR56-CPP compliant
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
#include <vector>

// ... definitions for S, T, globI, globD ...
template <typename Iter>
void f(Iter i, Iter e) {
  for (; i != e; ++i) {
    std::cout << (*i)->i << std::endl;
  }
}

int main() {
  std::vector<S *> test{new T, new T, new T, new T, new T};
  f(test.cbegin(), test.cend());
  for (auto v : test) {
    delete v;
  }
}
