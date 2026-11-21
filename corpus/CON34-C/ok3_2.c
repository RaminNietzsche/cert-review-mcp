// corpus: CON34-C compliant
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

#include <Windows.h>
#include <stdio.h>

DWORD WINAPI child_thread(LPVOID v) {
  int *result = (int *)v;
  printf("Result: %d\n", *result);  /* Correctly prints 1 */
  return NULL;
}

int create_thread(HANDLE *tid) {
  /* Declare val as a thread-local value */
  __declspec(thread) int val = 1;
  *tid = create_thread(NULL, 0, child_thread, &val, 0, NULL);
  return *tid == NULL;
}

int main(void) {
  HANDLE tid;
 
  if (create_thread(&tid)) {
    /* Handle error */
  }
 
  if (WAIT_OBJECT_0 != WaitForSingleObject(tid, INFINITE)) {
    /* Handle error */
  }
  CloseHandle(tid);
 
  return 0;
}
