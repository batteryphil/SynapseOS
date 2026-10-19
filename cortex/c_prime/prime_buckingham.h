/*
 * Buckingham Pi Dimensional Homogeneity Guard - Native C99 Header
 * ===============================================================
 * Sub-microsecond physical unit validation for candidate symbolic programs.
 * Base 5-tuple in Z^5: [Mass (M), Length (L), Time (T), Current (I), Temp (Theta)]
 */

#ifndef PRIME_BUCKINGHAM_H
#define PRIME_BUCKINGHAM_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int16_t m;   /* Mass */
    int16_t l;   /* Length */
    int16_t t;   /* Time */
    int16_t i;   /* Current */
    int16_t th;  /* Temperature */
} dim5_t;

static inline dim5_t dim5_zero(void) {
    dim5_t d = {0, 0, 0, 0, 0};
    return d;
}

static inline int dim5_is_equal(dim5_t a, dim5_t b) {
    return (a.m == b.m && a.l == b.l && a.t == b.t && a.i == b.i && a.th == b.th);
}

static inline int dim5_is_zero(dim5_t a) {
    return (a.m == 0 && a.l == 0 && a.t == 0 && a.i == 0 && a.th == 0);
}

static inline dim5_t dim5_add(dim5_t a, dim5_t b) {
    dim5_t r = { (int16_t)(a.m + b.m), (int16_t)(a.l + b.l), (int16_t)(a.t + b.t), (int16_t)(a.i + b.i), (int16_t)(a.th + b.th) };
    return r;
}

static inline dim5_t dim5_sub(dim5_t a, dim5_t b) {
    dim5_t r = { (int16_t)(a.m - b.m), (int16_t)(a.l - b.l), (int16_t)(a.t - b.t), (int16_t)(a.i - b.i), (int16_t)(a.th - b.th) };
    return r;
}

/*
 * Evaluates an RPN sequence for dimensional homogeneity.
 * Returns 1 if valid, 0 if physically incompatible.
 */
int prime_check_dimensional_homogeneity(
    const int *rpn,
    int rpn_len,
    const dim5_t *var_dims,
    int num_vars,
    const dim5_t *target_dim
);

/*
 * Benchmarks dimensional validation throughput in pure C.
 * Generates and evaluates num_candidates random symbolic trees.
 */
double prime_buckingham_benchmark(int num_candidates, int *out_vetoed);

#ifdef __cplusplus
}
#endif

#endif /* PRIME_BUCKINGHAM_H */
