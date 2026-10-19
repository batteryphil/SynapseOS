/*
 * PRIME Moment Attention: Zero-Dependency C99 Native Implementation
 * =================================================================
 * Constant-state O(1) second-order recurrent attention operator.
 * Supports:
 *   - Baseline second-order Taylor polynomial attention
 *   - Gated Delta-PRIME decoupled erase/write error delta updates
 *   - Dual-state Lyapunov contractive norm projection
 *   - Second-order Harmonic Phasor RoPE
 */

#include "prime_moment.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_STACK_HEAD_DIM 512

prime_config_t prime_default_config(int num_heads, int head_dim) {
    prime_config_t cfg;
    cfg.num_heads = num_heads;
    cfg.head_dim = head_dim;
    cfg.decay = 0.9995f;
    cfg.eps = 1e-4f;
    cfg.use_qk_norm = 0;
    cfg.use_delta_rule = 1;
    cfg.lyapunov_bound = 25.0f;
    cfg.use_harmonic_rope = 0;
    return cfg;
}

prime_state_t* prime_state_create(int num_heads, int head_dim) {
    if (num_heads <= 0 || head_dim <= 0) {
        return NULL;
    }

    prime_state_t *state = (prime_state_t*)malloc(sizeof(prime_state_t));
    if (!state) return NULL;

    state->num_heads = num_heads;
    state->head_dim = head_dim;

    size_t s0_size = (size_t)num_heads * head_dim * sizeof(float);
    size_t s1_size = (size_t)num_heads * head_dim * head_dim * sizeof(float);
    size_t s2_size = (size_t)num_heads * head_dim * head_dim * sizeof(float);
    size_t k0_size = (size_t)num_heads * sizeof(float);
    size_t k1_size = (size_t)num_heads * head_dim * sizeof(float);
    size_t k2_size = (size_t)num_heads * head_dim * sizeof(float);

    state->state_bytes = s0_size + s1_size + s2_size + k0_size + k1_size + k2_size;

    state->s0 = (float*)malloc(s0_size);
    state->s1 = (float*)malloc(s1_size);
    state->s2 = (float*)malloc(s2_size);
    state->k0 = (float*)malloc(k0_size);
    state->k1 = (float*)malloc(k1_size);
    state->k2 = (float*)malloc(k2_size);

    if (!state->s0 || !state->s1 || !state->s2 || !state->k0 || !state->k1 || !state->k2) {
        prime_state_free(state);
        return NULL;
    }

    prime_state_reset(state);
    return state;
}

void prime_state_reset(prime_state_t *state) {
    if (!state) return;
    int H = state->num_heads;
    int D = state->head_dim;

    memset(state->s0, 0, (size_t)H * D * sizeof(float));
    memset(state->s1, 0, (size_t)H * D * D * sizeof(float));
    memset(state->s2, 0, (size_t)H * D * D * sizeof(float));
    memset(state->k0, 0, (size_t)H * sizeof(float));
    memset(state->k1, 0, (size_t)H * D * sizeof(float));
    memset(state->k2, 0, (size_t)H * D * sizeof(float));
}

void prime_state_free(prime_state_t *state) {
    if (!state) return;
    if (state->s0) free(state->s0);
    if (state->s1) free(state->s1);
    if (state->s2) free(state->s2);
    if (state->k0) free(state->k0);
    if (state->k1) free(state->k1);
    if (state->k2) free(state->k2);
    free(state);
}

void prime_lyapunov_project(prime_state_t *state, float bound) {
    if (!state || bound <= 0.0f) return;
    int H = state->num_heads;
    int D = state->head_dim;
    int D2 = D * D;

    for (int h = 0; h < H; h++) {
        float *s1_head = state->s1 + h * D2;
        float *s2_head = state->s2 + h * D2;

        /* S1 Frobenius norm */
        float s1_sum = 0.0f;
        for (int i = 0; i < D2; i++) s1_sum += s1_head[i] * s1_head[i];
        float s1_norm = sqrtf(s1_sum);
        if (s1_norm > bound) {
            float scale1 = bound / (s1_norm + 1e-6f);
            for (int i = 0; i < D2; i++) s1_head[i] *= scale1;
        }

        /* S2 Frobenius norm */
        float s2_sum = 0.0f;
        for (int i = 0; i < D2; i++) s2_sum += s2_head[i] * s2_head[i];
        float s2_norm = sqrtf(s2_sum);
        if (s2_norm > bound) {
            float scale2 = bound / (s2_norm + 1e-6f);
            for (int i = 0; i < D2; i++) s2_head[i] *= scale2;
        }
    }
}

void prime_apply_harmonic_rope(
    float *q, float *k, float *q2, float *k2,
    int head_dim, int pos, float base_freq
) {
    for (int j = 0; j < head_dim; j += 2) {
        float freq = 1.0f / powf(base_freq, (float)j / (float)head_dim);
        float angle1 = (float)pos * freq;
        float cos1 = cosf(angle1);
        float sin1 = sinf(angle1);

        /* 1st harmonic on (q, k) */
        float q_re = q[j], q_im = q[j + 1];
        q[j]     = q_re * cos1 - q_im * sin1;
        q[j + 1] = q_re * sin1 + q_im * cos1;

        float k_re = k[j], k_im = k[j + 1];
        k[j]     = k_re * cos1 - k_im * sin1;
        k[j + 1] = k_re * sin1 + k_im * cos1;

        /* 2nd harmonic on (q^2, k^2) */
        float angle2 = 2.0f * angle1;
        float cos2 = cosf(angle2);
        float sin2 = sinf(angle2);

        float q2_re = q2[j], q2_im = q2[j + 1];
        q2[j]     = q2_re * cos2 - q2_im * sin2;
        q2[j + 1] = q2_re * sin2 + q2_im * cos2;

        float k2_re = k2[j], k2_im = k2[j + 1];
        k2[j]     = k2_re * cos2 - k2_im * sin2;
        k2[j + 1] = k2_re * sin2 + k2_im * cos2;
    }
}

static void apply_layer_norm(const float *src, float *dst, int dim) {
    float sum = 0.0f;
    for (int i = 0; i < dim; i++) sum += src[i];
    float mean = sum / (float)dim;

    float sq_diff_sum = 0.0f;
    for (int i = 0; i < dim; i++) {
        float diff = src[i] - mean;
        sq_diff_sum += diff * diff;
    }
    float variance = sq_diff_sum / (float)dim;
    float inv_std = 1.0f / sqrtf(variance + 1e-5f);

    for (int i = 0; i < dim; i++) {
        dst[i] = (src[i] - mean) * inv_std;
    }
}

void prime_step_delta(
    const prime_config_t *cfg,
    prime_state_t *state,
    const float *q_in,
    const float *k_in,
    const float *v_in,
    const float *b_gate,
    const float *w_gate,
    float *out
) {
    int H = cfg->num_heads;
    int D = cfg->head_dim;
    float decay = cfg->decay;
    float eps = cfg->eps;
    float inv_sqrt_d = 1.0f / sqrtf((float)D);

    float q_buf[MAX_STACK_HEAD_DIM];
    float k_buf[MAX_STACK_HEAD_DIM];
    float k_sq[MAX_STACK_HEAD_DIM];
    float q_sq[MAX_STACK_HEAD_DIM];
    float num[MAX_STACK_HEAD_DIM];
    float error_t[MAX_STACK_HEAD_DIM];

    for (int h = 0; h < H; h++) {
        const float *qh_in = q_in + h * D;
        const float *kh_in = k_in + h * D;
        const float *vh = v_in + h * D;
        float *out_h = out + h * D;

        float *s0 = state->s0 + h * D;
        float *s1 = state->s1 + h * D * D;
        float *s2 = state->s2 + h * D * D;
        float *k0 = state->k0 + h;
        float *k1 = state->k1 + h * D;
        float *k2 = state->k2 + h * D;

        if (cfg->use_qk_norm) {
            apply_layer_norm(qh_in, q_buf, D);
            apply_layer_norm(kh_in, k_buf, D);
        } else {
            memcpy(q_buf, qh_in, D * sizeof(float));
            memcpy(k_buf, kh_in, D * sizeof(float));
        }

        /* Scale queries */
        for (int d = 0; d < D; d++) {
            q_buf[d] *= inv_sqrt_d;
            q_sq[d] = q_buf[d] * q_buf[d];
            k_sq[d] = k_buf[d] * k_buf[d];
        }

        /* -------------------------------------------------------------
         * Mode 1: Gated Delta-PRIME Recurrence
         * ------------------------------------------------------------- */
        if (cfg->use_delta_rule) {
            /* 1. Predict value: v_hat = S0 + S1 @ k + 0.5 * S2 @ (k^2) */
            for (int d = 0; d < D; d++) {
                float v_hat_d = s0[d];
                const float *s1_row = s1 + d * D;
                const float *s2_row = s2 + d * D;
                float sum1 = 0.0f;
                float sum2 = 0.0f;
                for (int e = 0; e < D; e++) {
                    sum1 += s1_row[e] * k_buf[e];
                    sum2 += s2_row[e] * k_sq[e];
                }
                v_hat_d += sum1 + 0.5f * sum2;
                error_t[d] = vh[d] - v_hat_d;
            }

            /* 2. Decoupled Erase / Write Gate application */
            for (int d = 0; d < D; d++) {
                float b_d = b_gate ? b_gate[h * D + d] : 0.05f;
                float w_d = w_gate ? w_gate[h * D + d] : 0.25f;
                float erase_factor = (1.0f - b_d);
                float gamma_b = decay * erase_factor;
                float delta_payload = w_d * error_t[d] * 0.1f;

                s0[d] = gamma_b * s0[d] + delta_payload;

                float *s1_row = s1 + d * D;
                float *s2_row = s2 + d * D;
                for (int e = 0; e < D; e++) {
                    s1_row[e] = gamma_b * s1_row[e] + delta_payload * k_buf[e];
                    s2_row[e] = gamma_b * s2_row[e] + delta_payload * k_sq[e];
                }
            }

            /* 3. Output Readout: out = S0 + q @ S1 + 0.5 * q^2 @ S2 */
            for (int d = 0; d < D; d++) {
                float term1 = 0.0f;
                float term2 = 0.0f;
                for (int e = 0; e < D; e++) {
                    term1 += q_buf[e] * s1[e * D + d];
                    term2 += q_sq[e] * s2[e * D + d];
                }
                out_h[d] = s0[d] + term1 + 0.5f * term2;
            }

        /* -------------------------------------------------------------
         * Mode 2: Standard Additive Moment Recurrence
         * ------------------------------------------------------------- */
        } else {
            *k0 = decay * (*k0) + 1.0f;
            for (int d = 0; d < D; d++) {
                s0[d] = decay * s0[d] + vh[d];
                k1[d] = decay * k1[d] + k_buf[d];
                k2[d] = decay * k2[d] + k_sq[d];

                float *s1_col = s1 + d * D;
                float *s2_col = s2 + d * D;
                float v_val = vh[d];
                for (int e = 0; e < D; e++) {
                    s1_col[e] = decay * s1_col[e] + k_buf[e] * v_val;
                    s2_col[e] = decay * s2_col[e] + k_sq[e] * v_val;
                }
            }

            for (int d = 0; d < D; d++) num[d] = s0[d];
            for (int d = 0; d < D; d++) {
                float qd = q_buf[d];
                float q2d = 0.5f * q_sq[d];
                const float *s1_row = s1 + d * D;
                const float *s2_row = s2 + d * D;
                for (int e = 0; e < D; e++) {
                    num[e] += qd * s1_row[e] + q2d * s2_row[e];
                }
            }

            float den = *k0;
            for (int d = 0; d < D; d++) {
                den += q_buf[d] * k1[d] + 0.5f * q_sq[d] * k2[d];
            }
            if (den < eps) den = eps;
            float inv_den = 1.0f / den;
            for (int d = 0; d < D; d++) {
                out_h[d] = num[d] * inv_den;
            }
        }
    }

    /* 4. Dual-state Lyapunov contractive projection */
    if (cfg->lyapunov_bound > 0.0f) {
        prime_lyapunov_project(state, cfg->lyapunov_bound);
    }
}

void prime_step(
    const prime_config_t *cfg,
    prime_state_t *state,
    const float *q_in,
    const float *k_in,
    const float *v_in,
    float *out
) {
    prime_step_delta(cfg, state, q_in, k_in, v_in, NULL, NULL, out);
}

void prime_prefill(
    const prime_config_t *cfg,
    prime_state_t *state,
    int seq_len,
    const float *q_seq,
    const float *k_seq,
    const float *v_seq,
    float *out_seq
) {
    int stride = cfg->num_heads * cfg->head_dim;
    for (int t = 0; t < seq_len; t++) {
        prime_step(
            cfg,
            state,
            q_seq + t * stride,
            k_seq + t * stride,
            v_seq + t * stride,
            out_seq + t * stride
        );
    }
}
