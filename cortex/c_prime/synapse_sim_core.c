/*
 * SynapseOS C99 Simulation & Neural Engine (synapse_sim_core.c)
 * =============================================================
 * High-speed C99 physics, Lidar raycasting, Boids O(N^2) swarm intelligence,
 * 2-layer MLP backpropagation, CartPole dynamics, Lunar Lander physics,
 * and NEAT topological feed-forward evaluation.
 *
 * Compatible with:
 *   1. Native GCC/Clang (-O3 -fPIC -shared -> libsynapse_core.so)
 *   2. Fil-C Memory-Safe Cosmopolitan Libc (filcc --filc-cosmo --filc-ape)
 *   3. Cosmopolitan Libc (cosmocc -> .com APE)
 */

#include "synapse_sim_core.h"
#include <math.h>
#include <stddef.h>

static float clampf(float v, float lo, float hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static unsigned int xorshift32(unsigned int* state) {
    unsigned int x = *state;
    if (x == 0) x = 2463534242U;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return x;
}

static float rand_uniform(unsigned int* state, float lo, float hi) {
    unsigned int r = xorshift32(state);
    float u = (float)(r & 0x00FFFFFFU) / (float)0x01000000U;
    return lo + u * (hi - lo);
}

/* ============================================================================
 * 1. LAB 5: 2D MLP Neural Playground Forward & Analytical Backprop Kernel
 * ============================================================================ */
float synapse_mlp_predict(
    float x,
    float y,
    int hidden_neurons,
    int feat_count,
    float activation_gain,
    const float* w1,
    const float* b1,
    const float* w2,
    float b2,
    float* out_h_acts
) {
    float feats[4];
    feats[0] = x;
    feats[1] = y;
    feats[2] = (feat_count >= 3) ? (x * x + y * y) : 0.0f;
    feats[3] = (feat_count >= 4) ? (x * y) : 0.0f;

    float z_out = b2;
    for (int j = 0; j < hidden_neurons; ++j) {
        const float* w1_row = &w1[j * 4];
        float s = b1[j]
            + w1_row[0] * feats[0]
            + w1_row[1] * feats[1]
            + w1_row[2] * feats[2]
            + w1_row[3] * feats[3];
        float scaled = clampf(s * activation_gain, -15.0f, 15.0f);
        float hj = tanhf(scaled);
        if (out_h_acts != NULL) {
            out_h_acts[j] = hj;
        }
        z_out += w2[j] * hj;
    }
    z_out = clampf(z_out, -20.0f, 20.0f);
    return 1.0f / (1.0f + expf(-z_out));
}

void synapse_mlp_train_epochs(
    int num_epochs,
    int n_samples,
    const float* samples_x,
    const float* samples_y,
    const float* samples_label,
    int hidden_neurons,
    int feat_count,
    float activation_gain,
    float learning_rate,
    float l2_reg,
    float* w1,
    float* b1,
    float* w2,
    float* b2,
    float* out_loss,
    float* out_acc
) {
    if (n_samples <= 0 || hidden_neurons <= 0 || hidden_neurons > 64) {
        return;
    }
    float dw1[64 * 4];
    float db1[64];
    float dw2[64];
    float h_acts[64];
    float inv_n = 1.0f / (float)n_samples;
    float last_loss = 0.693f;
    float last_acc = 50.0f;

    for (int ep = 0; ep < num_epochs; ++ep) {
        for (int j = 0; j < hidden_neurons; ++j) {
            db1[j] = 0.0f;
            dw2[j] = 0.0f;
            for (int k = 0; k < 4; ++k) {
                dw1[j * 4 + k] = 0.0f;
            }
        }
        float db2_acc = 0.0f;
        float total_loss = 0.0f;
        int correct = 0;

        for (int i = 0; i < n_samples; ++i) {
            float x = samples_x[i];
            float y = samples_y[i];
            float target = samples_label[i];
            float feats[4];
            feats[0] = x;
            feats[1] = y;
            feats[2] = x * x + y * y;
            feats[3] = x * y;

            float prob = synapse_mlp_predict(
                x, y, hidden_neurons, feat_count, activation_gain,
                w1, b1, w2, *b2, h_acts
            );

            const float eps = 1e-7f;
            total_loss += -(target * logf(prob + eps) + (1.0f - target) * logf(1.0f - prob + eps));
            if ((prob >= 0.5f) == (target >= 0.5f)) {
                correct += 1;
            }

            float dz2 = (prob - target) * inv_n;
            db2_acc += dz2;
            for (int j = 0; j < hidden_neurons; ++j) {
                float hj = h_acts[j];
                dw2[j] += dz2 * hj;
                float dh = dz2 * w2[j] * (1.0f - hj * hj);
                db1[j] += dh;
                float* dw1_row = &dw1[j * 4];
                dw1_row[0] += dh * feats[0];
                dw1_row[1] += dh * feats[1];
                dw1_row[2] += dh * feats[2];
                dw1_row[3] += dh * feats[3];
            }
        }

        *b2 -= learning_rate * db2_acc;
        for (int j = 0; j < hidden_neurons; ++j) {
            w2[j] -= learning_rate * (dw2[j] + l2_reg * w2[j]);
            b1[j] -= learning_rate * db1[j];
            float* w1_row = &w1[j * 4];
            const float* dw1_row = &dw1[j * 4];
            for (int k = 0; k < 4; ++k) {
                w1_row[k] -= learning_rate * (dw1_row[k] + l2_reg * w1_row[k]);
            }
        }

        last_loss = total_loss * inv_n;
        last_acc = ((float)correct * 100.0f) * inv_n;
    }

    if (out_loss != NULL) *out_loss = last_loss;
    if (out_acc != NULL) *out_acc = last_acc;
}

/* ============================================================================
 * 2. LAB 2: 5-Beam Lidar Raycast & Parametric Circuit Distance Kernel
 * ============================================================================ */
float synapse_track_dist(float px, float py, float cx, float cy) {
    float dx = px - cx;
    float dy = py - cy;
    float theta = atan2f(dy, dx);
    float rx = 220.0f + 35.0f * cosf(2.0f * theta);
    float ry = 135.0f + 25.0f * sinf(3.0f * theta);
    float tx = cx + rx * cosf(theta);
    float ty = cy + ry * sinf(theta);
    return hypotf(px - tx, py - ty);
}

void synapse_car_cast_rays(
    float car_x,
    float car_y,
    float car_heading,
    float cx,
    float cy,
    float max_range,
    float half_width,
    float* out_ray_end_x,
    float* out_ray_end_y,
    float* out_norm_dist,
    float* out_obs_inputs
) {
    static const float RAY_ANGLES[5] = {-1.05f, -0.52f, 0.0f, 0.52f, 1.05f};
    const float step = 10.0f;
    float inv_max = (max_range > 1e-4f) ? (1.0f / max_range) : 1.0f;

    for (int i = 0; i < 5; ++i) {
        float ang = car_heading + RAY_ANGLES[i];
        float ca = cosf(ang);
        float sa = sinf(ang);
        float dist = 0.0f;
        while (dist < max_range) {
            dist += step;
            float rx = car_x + ca * dist;
            float ry = car_y + sa * dist;
            if (synapse_track_dist(rx, ry, cx, cy) > half_width) {
                break;
            }
        }
        float rx = car_x + ca * dist;
        float ry = car_y + sa * dist;
        float nd = clampf(dist * inv_max, 0.0f, 1.0f);
        out_ray_end_x[i] = rx;
        out_ray_end_y[i] = ry;
        out_norm_dist[i] = nd;
        out_obs_inputs[i] = nd * 2.0f - 1.0f;
    }
}

/* ============================================================================
 * 3. LAB 6: O(N^2) Predator-Prey Boids Swarm Physics Kernel
 * ============================================================================ */
void synapse_swarm_step(
    int n_prey,
    float* prey_x,
    float* prey_y,
    float* prey_vx,
    float* prey_vy,
    float* prey_energy,
    float* prey_score,
    const float* prey_genes,
    int n_pred,
    float* pred_x,
    float* pred_y,
    float* pred_vx,
    float* pred_vy,
    float* pred_score,
    const float* pred_genes,
    int n_food,
    float* food_x,
    float* food_y,
    float width,
    float height,
    float vision_radius,
    float prey_speed,
    float pred_speed,
    unsigned int rng_seed
) {
    unsigned int rng = rng_seed ? rng_seed : 1337U;
    const float margin = 35.0f;

    /* 1. Update Prey Flock */
    for (int i = 0; i < n_prey; ++i) {
        float px = prey_x[i];
        float py = prey_y[i];
        const float* genes = &prey_genes[i * 4];
        float fx = 0.0f;
        float fy = 0.0f;

        /* Nearest food attraction */
        if (n_food > 0) {
            int best_f = 0;
            float best_d2 = 1e30f;
            for (int f = 0; f < n_food; ++f) {
                float dx = food_x[f] - px;
                float dy = food_y[f] - py;
                float d2 = dx * dx + dy * dy;
                if (d2 < best_d2) {
                    best_d2 = d2;
                    best_f = f;
                }
            }
            float d = sqrtf(best_d2);
            if (d > 1e-3f && d < vision_radius * 1.4f) {
                fx += ((food_x[best_f] - px) / d) * genes[0];
                fy += ((food_y[best_f] - py) / d) * genes[0];
            }
            if (d < 10.0f) {
                prey_score[i] += 15.0f;
                prey_energy[i] = clampf(prey_energy[i] + 25.0f, 0.0f, 150.0f);
                food_x[best_f] = rand_uniform(&rng, 25.0f, width - 25.0f);
                food_y[best_f] = rand_uniform(&rng, 25.0f, height - 25.0f);
            }
        }

        /* Predator evasion */
        for (int p = 0; p < n_pred; ++p) {
            float dx = pred_x[p] - px;
            float dy = pred_y[p] - py;
            float d = hypotf(dx, dy);
            if (d > 1e-3f && d < vision_radius) {
                float w = (vision_radius / d) * genes[1];
                fx -= (dx / d) * w;
                fy -= (dy / d) * w;
            }
        }

        /* Flock separation & cohesion */
        float coh_limit = vision_radius * 0.7f;
        for (int j = 0; j < n_prey; ++j) {
            if (i == j) continue;
            float dx = prey_x[j] - px;
            float dy = prey_y[j] - py;
            float d = hypotf(dx, dy);
            if (d > 1e-3f && d < 22.0f) {
                fx -= (dx / d) * genes[3];
                fy -= (dy / d) * genes[3];
            } else if (d >= 22.0f && d < coh_limit) {
                fx += (dx / d) * (genes[2] * 0.15f);
                fy += (dy / d) * (genes[2] * 0.15f);
            }
        }

        /* Soft wall repulsion */
        if (px < margin) fx += 1.5f;
        else if (px > width - margin) fx -= 1.5f;
        if (py < margin) fy += 1.5f;
        else if (py > height - margin) fy -= 1.5f;

        float vx = prey_vx[i] * 0.85f + fx * 0.45f;
        float vy = prey_vy[i] * 0.85f + fy * 0.45f;
        float spd = hypotf(vx, vy);
        if (spd > prey_speed && spd > 1e-5f) {
            vx = (vx / spd) * prey_speed;
            vy = (vy / spd) * prey_speed;
        }
        prey_vx[i] = vx;
        prey_vy[i] = vy;
        prey_x[i] = clampf(px + vx, 8.0f, width - 8.0f);
        prey_y[i] = clampf(py + vy, 8.0f, height - 8.0f);
        prey_score[i] += 0.1f;
    }

    /* 2. Update Predators */
    for (int p = 0; p < n_pred; ++p) {
        float prx = pred_x[p];
        float pry = pred_y[p];
        float fx = 0.0f;
        float fy = 0.0f;
        if (n_prey > 0) {
            int best_idx = 0;
            float best_d2 = 1e30f;
            for (int i = 0; i < n_prey; ++i) {
                float dx = prey_x[i] - prx;
                float dy = prey_y[i] - pry;
                float d2 = dx * dx + dy * dy;
                if (d2 < best_d2) {
                    best_d2 = d2;
                    best_idx = i;
                }
            }
            float d = sqrtf(best_d2);
            if (d > 1e-3f) {
                fx += ((prey_x[best_idx] - prx) / d) * pred_genes[p * 4 + 0];
                fy += ((prey_y[best_idx] - pry) / d) * pred_genes[p * 4 + 0];
            }
            if (d < 11.0f) {
                pred_score[p] += 25.0f;
                float ns = prey_score[best_idx] - 12.0f;
                prey_score[best_idx] = (ns > 0.0f) ? ns : 0.0f;
                prey_x[best_idx] = rand_uniform(&rng, 40.0f, width - 40.0f);
                prey_y[best_idx] = rand_uniform(&rng, 40.0f, height - 40.0f);
            }
        }
        float vx = pred_vx[p] * 0.88f + fx * 0.42f;
        float vy = pred_vy[p] * 0.88f + fy * 0.42f;
        float spd = hypotf(vx, vy);
        if (spd > pred_speed && spd > 1e-5f) {
            vx = (vx / spd) * pred_speed;
            vy = (vy / spd) * pred_speed;
        }
        pred_vx[p] = vx;
        pred_vy[p] = vy;
        pred_x[p] = clampf(prx + vx, 8.0f, width - 8.0f);
        pred_y[p] = clampf(pry + vy, 8.0f, height - 8.0f);
    }
}

/* ============================================================================
 * 4. LAB 4: CartPole Non-Linear Euler-Lagrange Physics Step Kernel
 * ============================================================================ */
int synapse_cartpole_step(
    float* x,
    float* vx,
    float* theta,
    float* v_theta,
    float* fitness,
    int* steps,
    int max_steps,
    float force,
    float gravity,
    float pole_length,
    float x_threshold,
    float theta_threshold
) {
    const float dt = 0.02f;
    const float mass_cart = 1.0f;
    const float mass_pole = 0.1f;
    const float total_mass = mass_cart + mass_pole;
    float polemass_length = mass_pole * pole_length;

    *steps += 1;

    float cos_t = cosf(*theta);
    float sin_t = sinf(*theta);
    float vt = *v_theta;
    float temp = (force + polemass_length * vt * vt * sin_t) / total_mass;
    float theta_acc = (gravity * sin_t - cos_t * temp)
        / (pole_length * (4.0f / 3.0f - mass_pole * cos_t * cos_t / total_mass));
    float x_acc = temp - polemass_length * theta_acc * cos_t / total_mass;

    *x += dt * (*vx);
    *vx += dt * x_acc;
    *theta += dt * vt;
    *v_theta += dt * theta_acc;

    float center_bonus = 1.0f - (fabsf(*x) / x_threshold) * 0.5f;
    float upright_bonus = 1.0f - (fabsf(*theta) / theta_threshold) * 0.7f;
    *fitness += center_bonus + upright_bonus;

    if (fabsf(*x) > x_threshold || fabsf(*theta) > theta_threshold || *steps >= max_steps) {
        return 0; /* agent terminated */
    }
    return 1; /* agent still alive */
}

/* ============================================================================
 * 5. LAB 1: Rocket Moon Lander Physics, Shaping & Terrain Collision Kernel
 * ============================================================================ */
static float lander_shaping(
    float rx, float ry, float vx, float vy, float angle,
    float width, float height, float pad_x, float pad_y
) {
    float dx = (rx - pad_x) / (width * 0.5f);
    float dy = (pad_y - ry) / height;
    float dist = sqrtf(dx * dx + dy * dy);
    float speed = sqrtf(vx * vx + vy * vy) / 6.0f;
    float tilt = fabsf(angle) / 1.2f;
    return -110.0f * dist - 45.0f * speed - 35.0f * tilt;
}

static float lander_terrain_height(float x, float width, float pad_x, float pad_y, float pad_half_w) {
    float tx[12];
    float ty[12];
    tx[0] = 0.0f;   ty[0] = 330.0f;
    tx[1] = 55.0f;  ty[1] = 355.0f;
    tx[2] = 110.0f; ty[2] = 315.0f;
    tx[3] = 175.0f; ty[3] = 360.0f;
    tx[4] = 235.0f; ty[4] = 345.0f;
    tx[5] = pad_x - pad_half_w; ty[5] = pad_y;
    tx[6] = pad_x + pad_half_w; ty[6] = pad_y;
    tx[7] = 415.0f; ty[7] = 340.0f;
    tx[8] = 480.0f; ty[8] = 362.0f;
    tx[9] = 545.0f; ty[9] = 318.0f;
    tx[10] = 600.0f; ty[10] = 350.0f;
    tx[11] = 640.0f; ty[11] = 335.0f;

    float cx = clampf(x, 0.0f, width);
    for (int i = 0; i < 11; ++i) {
        if (cx >= tx[i] && cx <= tx[i + 1]) {
            float denom = tx[i + 1] - tx[i];
            if (denom < 1e-5f) denom = 1e-5f;
            float t = (cx - tx[i]) / denom;
            return ty[i] + t * (ty[i + 1] - ty[i]);
        }
    }
    return pad_y;
}

int synapse_lander_step(
    float* x,
    float* y,
    float* vx,
    float* vy,
    float* angle,
    float* v_angle,
    float* fuel,
    float* prev_shaping,
    float* total_reward,
    int* steps,
    int max_steps,
    int main_thruster,
    int left_thruster,
    int right_thruster,
    float gravity,
    float wind,
    float thruster_power,
    float landing_bonus,
    float width,
    float height,
    float pad_x,
    float pad_y,
    float pad_half_w,
    int* out_landed,
    int* out_crashed
) {
    const float dt = 0.12f;
    float g_acc = gravity * 0.45f;
    float wind_acc = wind * 0.25f;
    *steps += 1;
    *out_landed = 0;
    *out_crashed = 0;

    float ax = wind_acc;
    float ay = g_acc;

    if (main_thruster && *fuel > 0.0f) {
        float base_g = (g_acc > 0.7f) ? g_acc : 0.7f;
        float thrust = thruster_power * base_g;
        ax += sinf(*angle) * thrust;
        ay -= cosf(*angle) * thrust;
        *fuel = (*fuel > 0.55f) ? (*fuel - 0.55f) : 0.0f;
        *total_reward -= 0.04f;
    }

    if (left_thruster && *fuel > 0.0f) {
        *v_angle += 0.045f;
        *fuel = (*fuel > 0.15f) ? (*fuel - 0.15f) : 0.0f;
    } else if (right_thruster && *fuel > 0.0f) {
        *v_angle -= 0.045f;
        *fuel = (*fuel > 0.15f) ? (*fuel - 0.15f) : 0.0f;
    }

    *v_angle *= 0.92f;
    *angle += *v_angle;
    *vx += ax * dt;
    *vy += ay * dt;
    *x += *vx;
    *y += *vy;

    float new_shaping = lander_shaping(*x, *y, *vx, *vy, *angle, width, height, pad_x, pad_y);
    *total_reward += (new_shaping - *prev_shaping) - 0.06f;
    *prev_shaping = new_shaping;

    float ground_y = lander_terrain_height(*x, width, pad_x, pad_y, pad_half_w);
    if (*x < 15.0f || *x > width - 15.0f || *y < 10.0f) {
        *out_crashed = 1;
        *total_reward -= 110.0f;
        return 0; /* dead */
    } else if (*y >= ground_y - 10.0f) {
        *y = ground_y - 10.0f;
        int on_pad = (fabsf(*x - pad_x) <= pad_half_w);
        int soft_speed = (fabsf(*vx) < 1.65f && fabsf(*vy) < 2.15f);
        int upright = (fabsf(*angle) < 0.35f);
        if (on_pad && soft_speed && upright) {
            *out_landed = 1;
            *total_reward += landing_bonus + ((*fuel) * 0.25f);
        } else {
            *out_crashed = 1;
            *total_reward -= 75.0f;
        }
        return 0; /* landed or crashed */
    } else if (*steps >= max_steps) {
        *total_reward -= 25.0f;
        return 0; /* timeout */
    }
    return 1; /* alive */
}

/* ============================================================================
 * 6. NEAT Feed-Forward Topological Evaluation Kernel
 * ============================================================================ */
void synapse_neat_forward(
    int num_nodes,
    const float* node_biases,
    float* node_acts,
    int eval_start_idx,
    int num_conns,
    const int* conn_in_idx,
    const int* conn_out_idx,
    const float* conn_weights
) {
    for (int idx = eval_start_idx; idx < num_nodes; ++idx) {
        float s = node_biases[idx];
        for (int c = 0; c < num_conns; ++c) {
            if (conn_out_idx[c] == idx) {
                int in_idx = conn_in_idx[c];
                if (in_idx >= 0 && in_idx < num_nodes) {
                    s += node_acts[in_idx] * conn_weights[c];
                }
            }
        }
        s = clampf(s, -20.0f, 20.0f);
        node_acts[idx] = tanhf(s);
    }
}

/* ============================================================================
 * 7. BuildbitOS 1.58-Bit Ternary Bit-Sliced POPCNT & Mamba SSM Potato Kernels
 *    Ported from buildbit-os/os/os_superpowers.h & buildbit-os/os/mamba_engine.h
 *    100% Potato-Safe (Runs on any 2007+ x86_64 CPU with zero GPU or AVX2 needed)
 * ============================================================================ */
#include <stdint.h>
#include <stdlib.h>
#include <sys/time.h>

typedef struct {
    uint64_t pos_mask;
    uint64_t neg_mask;
} synapse_trit64_pack_t;

static double synapse_now_ms(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (double)tv.tv_sec * 1000.0 + (double)tv.tv_usec / 1000.0;
}

void synapse_trit64_bench(
    int dim,
    int n_tokens,
    float* out_fp32_ms,
    float* out_trit_ms,
    float* out_speedup,
    int* out_exact_match
) {
    if (dim < 64) dim = 64;
    dim = (dim / 64) * 64;
    if (n_tokens < 1) n_tokens = 1;
    int packs_per_row = dim / 64;
    size_t total_weights = (size_t)dim * (size_t)dim;

    float* w_fp32 = (float*)malloc(total_weights * sizeof(float));
    float* x_fp32 = (float*)malloc((size_t)n_tokens * (size_t)dim * sizeof(float));
    float* y_fp32 = (float*)malloc((size_t)n_tokens * (size_t)dim * sizeof(float));
    synapse_trit64_pack_t* w_trit = (synapse_trit64_pack_t*)malloc((size_t)dim * (size_t)packs_per_row * sizeof(synapse_trit64_pack_t));
    synapse_trit64_pack_t* x_trit = (synapse_trit64_pack_t*)malloc((size_t)n_tokens * (size_t)packs_per_row * sizeof(synapse_trit64_pack_t));
    int32_t* y_trit = (int32_t*)malloc((size_t)n_tokens * (size_t)dim * sizeof(int32_t));

    if (!w_fp32 || !x_fp32 || !y_fp32 || !w_trit || !x_trit || !y_trit) {
        free(w_fp32); free(x_fp32); free(y_fp32);
        free(w_trit); free(x_trit); free(y_trit);
        return;
    }

    for (int r = 0; r < dim; ++r) {
        for (int p = 0; p < packs_per_row; ++p) {
            uint64_t pm = 0ULL, nm = 0ULL;
            for (int b = 0; b < 64; ++b) {
                uint64_t idx = (uint64_t)r * (uint64_t)dim + (uint64_t)(p * 64 + b);
                int v = (int)((idx * 1103515245ULL + 12345ULL) % 3ULL) - 1;
                w_fp32[idx] = (float)v;
                if (v == 1)  pm |= (1ULL << b);
                if (v == -1) nm |= (1ULL << b);
            }
            w_trit[r * packs_per_row + p].pos_mask = pm;
            w_trit[r * packs_per_row + p].neg_mask = nm;
        }
    }

    for (int t = 0; t < n_tokens; ++t) {
        for (int p = 0; p < packs_per_row; ++p) {
            uint64_t pm = 0ULL, nm = 0ULL;
            for (int b = 0; b < 64; ++b) {
                uint64_t idx = (uint64_t)t * (uint64_t)dim + (uint64_t)(p * 64 + b);
                int v = (int)(((idx + 7ULL) * 2654435761ULL) % 3ULL) - 1;
                x_fp32[idx] = (float)v;
                if (v == 1)  pm |= (1ULL << b);
                if (v == -1) nm |= (1ULL << b);
            }
            x_trit[t * packs_per_row + p].pos_mask = pm;
            x_trit[t * packs_per_row + p].neg_mask = nm;
        }
    }

    double t0 = synapse_now_ms();
    for (int t = 0; t < n_tokens; ++t) {
        const float* xt = &x_fp32[t * dim];
        float* yt = &y_fp32[t * dim];
        for (int r = 0; r < dim; ++r) {
            const float* wr = &w_fp32[(size_t)r * (size_t)dim];
            float sum = 0.0f;
            for (int c = 0; c < dim; ++c) {
                sum += wr[c] * xt[c];
            }
            yt[r] = sum;
        }
    }
    double t1 = synapse_now_ms();

    double t2 = synapse_now_ms();
    for (int t = 0; t < n_tokens; ++t) {
        const synapse_trit64_pack_t* xt = &x_trit[t * packs_per_row];
        int32_t* yt = &y_trit[t * dim];
        for (int r = 0; r < dim; ++r) {
            const synapse_trit64_pack_t* wr = &w_trit[r * packs_per_row];
            int32_t acc = 0;
            for (int p = 0; p < packs_per_row; ++p) {
                uint64_t wp = wr[p].pos_mask;
                uint64_t wn = wr[p].neg_mask;
                uint64_t xp = xt[p].pos_mask;
                uint64_t xn = xt[p].neg_mask;
                int pos_hits = __builtin_popcountll((wp & xp) | (wn & xn));
                int neg_hits = __builtin_popcountll((wp & xn) | (wn & xp));
                acc += (pos_hits - neg_hits);
            }
            yt[r] = acc;
        }
    }
    double t3 = synapse_now_ms();

    float fp32_ms = (float)(t1 - t0);
    float trit_ms = (float)(t3 - t2);
    if (trit_ms < 0.001f) trit_ms = 0.001f;
    if (out_fp32_ms) *out_fp32_ms = fp32_ms;
    if (out_trit_ms) *out_trit_ms = trit_ms;
    if (out_speedup) *out_speedup = fp32_ms / trit_ms;
    if (out_exact_match) {
        int diff = (int)(y_fp32[0] >= 0.0f ? (y_fp32[0] + 0.5f) : (y_fp32[0] - 0.5f)) - (int)y_trit[0];
        *out_exact_match = (diff == 0) ? 1 : 0;
    }

    free(w_fp32); free(x_fp32); free(y_fp32);
    free(w_trit); free(x_trit); free(y_trit);
}

void synapse_mamba_ssm_bench(
    int d_inner,
    int n_tokens,
    float* out_scan_ms,
    float* out_tok_per_sec,
    float* out_state_kb
) {
    if (d_inner < 64) d_inner = 64;
    if (n_tokens < 1) n_tokens = 1;
    const int d_state = 16;

    float* h_state = (float*)calloc((size_t)d_inner * (size_t)d_state, sizeof(float));
    float* A_bar   = (float*)malloc((size_t)d_inner * (size_t)d_state * sizeof(float));
    float* B_u     = (float*)malloc((size_t)d_inner * (size_t)d_state * sizeof(float));
    float* C_vec   = (float*)malloc((size_t)d_state * sizeof(float));
    float* y_out   = (float*)malloc((size_t)d_inner * sizeof(float));

    if (!h_state || !A_bar || !B_u || !C_vec || !y_out) {
        free(h_state); free(A_bar); free(B_u); free(C_vec); free(y_out);
        return;
    }

    for (int i = 0; i < d_inner * d_state; ++i) {
        A_bar[i] = 0.96f;
        B_u[i]   = 0.04f * (float)((i & 7) - 3);
    }
    for (int s = 0; s < d_state; ++s) {
        C_vec[s] = 0.125f;
    }

    double t0 = synapse_now_ms();
    for (int t = 0; t < n_tokens; ++t) {
        for (int c = 0; c < d_inner; ++c) {
            float* hc = &h_state[c * d_state];
            const float* ac = &A_bar[c * d_state];
            const float* bc = &B_u[c * d_state];
            float acc = 0.0f;
            for (int s = 0; s < d_state; ++s) {
                float h_new = ac[s] * hc[s] + bc[s];
                hc[s] = h_new;
                acc += h_new * C_vec[s];
            }
            /* Fused SiLU gate */
            float sig = 1.0f / (1.0f + expf(-acc));
            y_out[c] = acc * sig;
        }
    }
    double t1 = synapse_now_ms();
    volatile float sink = y_out[0];
    (void)sink;

    float scan_ms = (float)(t1 - t0);
    if (scan_ms < 0.001f) scan_ms = 0.001f;
    if (out_scan_ms) *out_scan_ms = scan_ms;
    if (out_tok_per_sec) *out_tok_per_sec = ((float)n_tokens * 1000.0f) / scan_ms;
    if (out_state_kb) *out_state_kb = (float)((size_t)d_inner * (size_t)(d_state + 4) * sizeof(float)) / 1024.0f;

    free(h_state); free(A_bar); free(B_u); free(C_vec); free(y_out);
}

