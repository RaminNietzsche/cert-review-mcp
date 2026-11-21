// corpus: DCL59-CPP noncompliant
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

// a.h
#ifndef A_HEADER_FILE
#define A_HEADER_FILE
 
void f() { /* ... */ }
 
#endif // A_HEADER_FILE
 
// a.cpp
#include "a.h"
// ...
 
// b.cpp
#include "a.h"
// ...
