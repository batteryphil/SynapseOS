/*
 * Buckingham Pi Dimensional Homogeneity Guard - Native C99 Implementation
 * =======================================================================
 * Sub-microsecond physical unit validation for candidate symbolic programs.
 */

#define _POSIX_C_SOURCE 199309L
#include "prime_buckingham.h"
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
static double get_time_sec(void) {
    LARGE_INTEGER freq, count;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&count);
    return (double)count.QuadPart / (double)freq.QuadPart;
}
#else
static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}
#endif

int prime_check_dimensional_homogeneity(
    const int *rpn,
    int rpn_len,
    const dim5_t *var_dims,
    int num_vars,
    const dim5_t *target_dim
) {
    dim5_t stack[32];
    int sp = 0;
    dim5_t zero = dim5_zero();

    for (int idx = 0; idx < rpn_len; idx++) {
        int token = rpn[idx];
        if (token == -1) break;

        /* Variable tokens: 0..9 */
        if (token >= 0 && token <= 9) {
            if (sp >= 32) return 0;
            if (token < num_vars && var_dims != NULL) {
                stack[sp++] = var_dims[token];
            } else {
                stack[sp++] = zero;
            }
        }
        /* Dimensionless Constants: 10, 11, 12 */
        else if (token >= 10 && token <= 12) {
            if (sp >= 32) return 0;
            stack[sp++] = zero;
        }
        /* Addition (20) or Subtraction (21): Dimensions MUST match exactly */
        else if (token == 20 || token == 21) {
            if (sp < 2) return 0;
            dim5_t b = stack[--sp];
            dim5_t a = stack[--sp];
            if (!dim5_is_equal(a, b)) return 0;
            stack[sp++] = a;
        }
        /* Multiplication (22): Exponent addition */
        else if (token == 22) {
            if (sp < 2) return 0;
            dim5_t b = stack[--sp];
            dim5_t a = stack[--sp];
            stack[sp++] = dim5_add(a, b);
        }
        /* Division (23): Exponent subtraction */
        else if (token == 23) {
            if (sp < 2) return 0;
            dim5_t b = stack[--sp];
            dim5_t a = stack[--sp];
            stack[sp++] = dim5_sub(a, b);
        }
        /* Transcendental (24..27): sin, cos, exp, log - Argument MUST be dimensionless */
        else if (token >= 24 && token <= 27) {
            if (sp < 1) return 0;
            dim5_t a = stack[--sp];
            if (!dim5_is_zero(a)) return 0;
            stack[sp++] = zero;
        }
        /* Sqrt (28): All exponents must be even */
        else if (token == 28) {
            if (sp < 1) return 0;
            dim5_t a = stack[--sp];
            if ((a.m % 2 != 0) || (a.l % 2 != 0) || (a.t % 2 != 0) || (a.i % 2 != 0) || (a.th % 2 != 0)) {
                return 0;
            }
            dim5_t res = { (int16_t)(a.m / 2), (int16_t)(a.l / 2), (int16_t)(a.t / 2), (int16_t)(a.i / 2), (int16_t)(a.th / 2) };
            stack[sp++] = res;
        }
        /* Square (29): Exponents doubled */
        else if (token == 29) {
            if (sp < 1) return 0;
            dim5_t a = stack[--sp];
            dim5_t res = { (int16_t)(a.m * 2), (int16_t)(a.l * 2), (int16_t)(a.t * 2), (int16_t)(a.i * 2), (int16_t)(a.th * 2) };
            stack[sp++] = res;
        }
        /* Unary Negation (30): Dimension unchanged */
        else if (token == 30) {
            if (sp < 1) return 0;
            /* stack top stays as-is */
        }
    }

    if (sp != 1) return 0;

    if (target_dim != NULL) {
        if (!dim5_is_equal(stack[0], *target_dim)) return 0;
    }

    return 1;
}

double prime_buckingham_benchmark(int num_candidates, int *out_vetoed) {
    /* NASA Battery Domain:
     * x0 = Voltage: M L^2 T^-3 I^-1 = [1, 2, -3, -1, 0]
     * x1 = Current: I = [0, 0, 0, 1, 0]
     * x2 = Time: T = [0, 0, 1, 0, 0]
     * x3 = Temp: Theta = [0, 0, 0, 0, 1]
     * Target = Capacity (Ah): I * T = [0, 0, 1, 1, 0]
     */
    dim5_t var_dims[4] = {
        {1, 2, -3, -1, 0},
        {0, 0, 0, 1, 0},
        {0, 0, 1, 0, 0},
        {0, 0, 0, 0, 1}
    };
    dim5_t target_cap = {0, 0, 1, 1, 0};

    int token_pool[12] = {0, 1, 2, 3, 10, 11, 20, 21, 22, 23, 26, 28};
    int pool_size = 12;

    int rpn_buf[16];
    int vetoed = 0;

    double t0 = get_time_sec();
    for (int n = 0; n < num_candidates; n++) {
        int len = 3 + (rand() % 5);
        for (int i = 0; i < len; i++) {
            rpn_buf[i] = token_pool[rand() % pool_size];
        }
        rpn_buf[len] = -1;

        int ok = prime_check_dimensional_homogeneity(rpn_buf, len, var_dims, 4, &target_cap);
        if (!ok) vetoed++;
    }
    double elapsed = get_time_sec() - t0;

    if (out_vetoed) *out_vetoed = vetoed;
    return elapsed;
}
