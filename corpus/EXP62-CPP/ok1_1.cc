// corpus: EXP62-CPP compliant
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

struct S {  
  unsigned char buffType;
  int size;
 
  friend bool operator==(const S &lhs, const S &rhs) {
    return lhs.buffType == rhs.buffType &&
           lhs.size == rhs.size;
  }
};
 
void f(const S &s1, const S &s2) {
  if (s1 == s2) {
    // ...
  }
}
