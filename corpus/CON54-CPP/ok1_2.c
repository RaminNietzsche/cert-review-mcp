// corpus: CON54-CPP compliant
#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <pthread.h>
#include <signal.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <wchar.h>

#include <condition_variable>
#include <mutex>
 
struct Node {
  void *node;
  struct Node *next;
};
  
static Node list;
static std::mutex m;
static std::condition_variable condition;
  
void consume_list_element() {
  std::unique_lock<std::mutex> lk(m);
 
  condition.wait(lk, []{ return list.next; });
  // Proceed when condition holds.
}
