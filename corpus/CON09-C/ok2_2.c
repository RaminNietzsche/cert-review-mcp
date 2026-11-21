// corpus: CON09-C compliant
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

#include <glib.h>
#include <glib-object.h>
 
void queue_enqueue(Queue *q, gpointer data) {
  Node *node;
  Node *tail;
  Node *next;

  node = g_slice_new(Node);
  node->data = data;
  node->next = NULL;
  while (TRUE) {
    tail = q->tail;
    HAZARD_SET(0, tail);  /* Mark tail as hazardous */
    if (tail != q->tail) {  /* Check tail hasn't changed */
      continue;
    }
    next = tail->next;
    if (tail != q->tail) {
      continue;
    }
    if (next != NULL) {
      CAS(&q->tail, tail, next);
      continue;
    }
    if (CAS(&tail->next, null, node) {
      break;
    }
  }
  CAS(&q->tail, tail, node);
}

gpointer queue_dequeue(Queue *q) {
  Node *node;
  Node *head;
  Node *tail;
  Node *next;
  gpointer data;

  while (TRUE) {
    head = q->head;
    LF_HAZARD_SET(0, head);  /* Mark head as hazardous */
    if (head != q->head) {  /* Check head hasn't changed */
      continue;
    }
    tail = q->tail;
    next = head->next;
    LF_HAZARD_SET(1, next);  /* Mark next as hazardous */
    if (head != q->head) {
      continue;
    }
    if (next == NULL) {
      return NULL; /* Empty */
    }
    if (head == tail) {
      CAS(&q->tail, tail, next);
      continue;
    }
    data = next->data;
    if (CAS(&q->head, head, next)) {
      break;
    }
  }
  LF_HAZARD_UNSET(head);  /*
                           * Retire head, and perform
                           * reclamation if needed.
                           */
  return data;
}
