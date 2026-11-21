// corpus: OOP50-CPP noncompliant
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

struct B {
  B() { seize(); }
  virtual ~B() { release(); }
 
protected:
  virtual void seize();
  virtual void release();
};

struct D : B {
  virtual ~D() = default;
 
protected:
  void seize() override {
    B::seize();
    // Get derived resources...
  }
 
  void release() override {
    // Release derived resources...
    B::release();
  }
};
