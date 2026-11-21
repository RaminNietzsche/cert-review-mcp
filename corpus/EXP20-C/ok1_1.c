// corpus: EXP20-C compliant
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

LinkedList bannedUsers;

int is_banned(User usr) {
  int x = 0;

  Node cur_node = (bannedUsers->head);

  while(cur_node != NULL) {
    if (strcmp((char *)cur_node->data, usr->name)==0) {
      x++;
    }
    cur_node = cur_node->next;
  }

  return x;
}

void processRequest(User usr) {
  if (is_banned(usr) != 0) {
    return;
  }
  serveResults();
}
