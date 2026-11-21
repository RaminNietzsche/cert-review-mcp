// corpus: MSC50-CPP noncompliant
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

#include <cstdlib>
#include <string>
 
void f() {
  std::string id("ID"); // Holds the ID, starting with the characters "ID" followed
                        // by a random integer in the range [0-10000].
  id += std::to_string(std::rand() % 10000);
  // ...
}
