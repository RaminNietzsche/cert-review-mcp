// corpus: DCL58-CPP compliant
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

#include <functional>
#include <iostream>
#include <string>
 
class MyString {
  std::string data;
   
public:
  MyString(const std::string &data) : data(data) {}
   
  const std::string &get_data() const { return data; }
};
 
namespace std {
template <>
struct plus<MyString> {
  MyString operator()(const MyString &lhs, const MyString &rhs) const {
    return lhs.get_data() + rhs.get_data();
  }
};
}
 
void f() {
  std::string s1("My String");
  MyString s2(" + Your String");
  std::plus<MyString> p;
   
  std::cout << p(s1, s2).get_data() << std::endl;
}
