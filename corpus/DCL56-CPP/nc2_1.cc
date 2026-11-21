// corpus: DCL56-CPP noncompliant
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

// file.h
#ifndef FILE_H
#define FILE_H
 
class Car {
  int numWheels;
 
public:
  Car() : numWheels(4) {}
  explicit Car(int numWheels) : numWheels(numWheels) {}
 
  int get_num_wheels() const { return numWheels; }
};
#endif // FILE_H
 
// file1.cpp
#include "file.h"
#include <iostream>
 
extern Car c;
int numWheels = c.get_num_wheels();
 
int main() {
  std::cout << numWheels << std::endl;
}
 
// file2.cpp
#include "file.h"
 
Car get_default_car() { return Car(6); }
Car c = get_default_car();
