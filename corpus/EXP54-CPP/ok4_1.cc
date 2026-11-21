// corpus: EXP54-CPP compliant
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
 
class C {
  std::vector<int> l;
  
public:
  C() : l{1, 2, 3} {}
  
  int first() const { return *l.begin(); }
};
 
void f() {
  C c;
  std::cout << c.first();
}
