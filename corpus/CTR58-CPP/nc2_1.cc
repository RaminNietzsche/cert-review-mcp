// corpus: CTR58-CPP noncompliant
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

#include <algorithm>
#include <iostream>
#include <iterator>
#include <vector>
  
template <typename Iter>
void print_container(Iter b, Iter e) {
  std::cout << "Contains: ";
  std::copy(b, e, std::ostream_iterator<decltype(*b)>(std::cout, " "));
  std::cout << std::endl;
}
 
void f() {
  std::vector<int> v{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
  print_container(v.begin(), v.end());

  int timesCalled = 0;
  v.erase(std::remove_if(v.begin(), v.end(), [timesCalled](const int &) mutable { return ++timesCalled == 3; }), v.end());
  print_container(v.begin(), v.end());
}
