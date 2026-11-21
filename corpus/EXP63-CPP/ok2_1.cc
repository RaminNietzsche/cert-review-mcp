// corpus: EXP63-CPP compliant
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
#include <iostream>
#include <vector>
 
void f(std::vector<int> &c) {
  auto e = std::remove(c.begin(), c.end(), 42);
  for (auto i = c.begin(); i != c.end(); i++) {
    if (i < e) {
      std::cout << *i << std::endl;
    }
  }
}
