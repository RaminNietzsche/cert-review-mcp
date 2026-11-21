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

#include <iostream>
#include <string>

void g(std::string v) {
  std::cout << v << std::endl;
}

void f() {
  for (unsigned i = 0; i < 10; ++i) {
    std::string s(1, static_cast<char>('0' + i));
    g(std::move(s));
  }
}
