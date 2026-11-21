// corpus: EXP56-CPP compliant
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

extern "java" typedef void (*java_callback)(int);

extern void call_java_fn_ptr(java_callback callback);
extern "java" void callback_func(int);

void f() {
  call_java_fn_ptr(callback_func);
}
