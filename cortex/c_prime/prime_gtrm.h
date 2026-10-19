/*
 * GTRM: Generative Thought Reconstruction Map - Native C99 Header
 * ===============================================================
 * Biomimetic 64 KB Constant-Memory Cognitive Layer.
 *
 * Distills cognitive trajectories into 32-dim topological blueprints (m_t),
 * gates consolidation with novelty detection (gamma_t), maintains a second-order
 * quadratic memory state M^(2) in R^(32 x D) (exactly 65.5 KB for D=512), and
 * dynamically reconstructs prior thoughts into the reasoning stream upon query.
 */

#ifndef PRIME_GTRM_H
#define PRIME_GTRM_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int d_model;        /* Embedding dimension D (e.g. 512) */
    int d_map;          /* Topological blueprint dimension (default: 32) */
    float decay;        /* Retention decay factor (default: 0.9995f) */
    float eps;          /* Normalization epsilon (default: 1e-4f) */
    size_t state_bytes; /* Memory state footprint: d_map * d_model * sizeof(float) */

    /* Second-order quadratic memory manifold M^(2): [d_map, d_model] */
    float *m2_state;

    /* Projections (stored as row-major flat buffers or initialized randomly) */
    float *w_map;       /* [d_map, d_model] */
    float *w_salience;  /* [d_model] */
    float *w_v;         /* [d_model, d_model] */
    float *w_q;         /* [d_map, d_model] */
    float *w_recon;     /* [d_model, d_model] */
} prime_gtrm_t;

/* Allocate and initialize GTRM layer */
prime_gtrm_t* prime_gtrm_create(int d_model, int d_map, float decay);

/* Reset quadratic memory manifold to zero */
void prime_gtrm_reset(prime_gtrm_t *gtrm);

/* Free allocated GTRM memory */
void prime_gtrm_free(prime_gtrm_t *gtrm);

/*
 * Single-step streaming thought consolidation & reconstruction (L == 1):
 * Ingests current hidden token x_in [d_model], updates 64 KB memory M^(2),
 * reconstructs prior cued thoughts, and returns updated representation out [d_model].
 */
void prime_gtrm_step(
    prime_gtrm_t *gtrm,
    const float *x_in,
    float *out
);

/*
 * High-speed multi-token prefill consolidation (L > 1) in pure C:
 * Consolidates sequence of L tokens into the 64 KB memory state.
 */
void prime_gtrm_prefill(
    prime_gtrm_t *gtrm,
    int seq_len,
    const float *x_seq,
    float *out_seq
);

#ifdef __cplusplus
}
#endif

#endif /* PRIME_GTRM_H */
