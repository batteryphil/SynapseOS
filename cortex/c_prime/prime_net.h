/*
 * PRIME-Net: Zero-Dependency C99 Symbolic Co-Thinker & Reasoning Engine
 * ====================================================================
 * High-performance, zero-allocation native implementation of PRIME-Net:
 * 1. Recursive-descent arithmetic evaluator (PEMDAS, powers, float decimals, negatives).
 * 2. Symbolic solvers: Quadratic equations, linear systems, percentages, sequences.
 * 3. Word-problem solvers: Proportions, rates/speeds, rectangular geometry, unit pricing.
 * 4. Associative retrieval: Entity-targeted NIAH passkey extraction with temporal preference.
 * 5. CoT generator: Produces structured <think> ... </think> reasoning trajectories.
 */

#ifndef PRIME_NET_H
#define PRIME_NET_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int found_invariant;
    char invariant_str[512];    /* Formatted invariant tag for <think> priming */
    char solution_str[128];     /* Pure numerical or string answer */
    char response_full[2048];   /* Complete generated response with <think> and final answer */
} prime_net_result_t;

/* Core reasoning pipeline */
prime_net_result_t prime_net_solve(const char *prompt);

/* Direct arithmetic expression evaluation */
int prime_net_eval_expr(const char *expr, double *out_val);

/* Comprehensive C test benchmarks */
int prime_net_run_math_benchmark(void);
int prime_net_run_niah_benchmark(void);
int prime_net_run_deduction_benchmark(void);

#ifdef __cplusplus
}
#endif

#endif /* PRIME_NET_H */
