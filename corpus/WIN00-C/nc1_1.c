// corpus: WIN00-C noncompliant
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
 
void func(void) {
  HMODULE hMod = LoadLibrary(TEXT("MyLibrary.dll"));
  if (hMod != NULL) {
    typedef void (__cdecl func_type)(void);
    func_type *fn = (func_type *)GetProcAddress(hMod, "MyFunction");
    if (fn != NULL)
      fn();
  }
}
