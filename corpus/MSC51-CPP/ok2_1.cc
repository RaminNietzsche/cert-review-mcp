// corpus: MSC51-CPP compliant
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

#include <random>
#include <iostream>

void f() {
  std::random_device dev;
  std::mt19937 engine(dev());
  
  for (int i = 0; i < 10; ++i) {
    std::cout << engine() << ", ";
  }
} 
