// corpus: INT30-C compliant
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

#include <stdckdint.h>

/* ... */

pen->num_vertices = _cairo_pen_vertices_needed(
  gstate->tolerance, radius, &gstate->ctm
);

size_t product;
if (ckd_mul(&product, pen->num_vertices, sizeof(cairo_pen_vertex_t))) {
  /* Handle error */
}

pen->vertices = malloc(product);
