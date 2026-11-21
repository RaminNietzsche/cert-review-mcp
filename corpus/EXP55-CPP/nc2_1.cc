// corpus: EXP55-CPP noncompliant
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
 
class S {
  int cachedValue;
  
  int compute_value() const;  // expensive
public:
  S() : cachedValue(0) {}
  
  // ...  
  int get_value() const {
    if (!cachedValue) {
      const_cast<S *>(this)->cachedValue = compute_value();  
    }        
    return cachedValue;
  }
};

void f() {
  const S s;
  std::cout << s.get_value() << std::endl;
}
