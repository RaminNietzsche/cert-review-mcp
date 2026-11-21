// corpus: ARR30-C compliant
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

HRESULT GetMachineName(
  wchar_t *pwszPath,
  wchar_t wszMachineName[MAX_COMPUTERNAME_LENGTH_FQDN+1])
{
  wchar_t *pwszServerName = wszMachineName;
  wchar_t *pwszTemp = pwszPath + 2;
  wchar_t *end_addr
    = pwszServerName + MAX_COMPUTERNAME_LENGTH_FQDN;
  while ((*pwszTemp != L'\\') &&
         (*pwszTemp != L'\0') &&
         (pwszServerName < end_addr))
  {
    *pwszServerName++ = *pwszTemp++;
  }

  /* ... */
}
