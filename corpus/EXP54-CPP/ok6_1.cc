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

class S { 
  int v; 
 
public: 
  S() : v(12) {} // Non-trivial constructor 
  
  void f(); 
};   
 
void f() { 
  S s; 
 
  // ... 
 
  goto bad_idea; 
 
  // ... 
 
  bad_idea: 
    s.f(); 
}
