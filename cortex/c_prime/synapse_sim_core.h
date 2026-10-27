#ifndef SYNAPSE_SIM_CORE_H
#define SYNAPSE_SIM_CORE_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * 1. LAB 5: 2D MLP Neural Playground Forward & Analytical Backprop Kernel
 * ============================================================================ */
float synapse_mlp_predict(
    float x,
    float y,
    int hidden_neurons,
    int feat_count,
    float activation_gain,
    const float* w1,   /* [hidden_neurons * 4] */
    const float* b1,   /* [hidden_neurons] */
    const float* w2,   /* [hidden_neurons] */
    float b2,
    float* out_h_acts  /* [hidden_neurons] */
);

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
    float* w1,         /* in/out [hidden_neurons * 4] */
    float* b1,         /* in/out [hidden_neurons] */
    float* w2,         /* in/out [hidden_neurons] */
    float* b2,         /* in/out [1] */
    float* out_loss,   /* out [1] */
    float* out_acc     /* out [1] */
);

/* ============================================================================
 * 2. LAB 2: 5-Beam Lidar Raycast & Parametric Circuit Distance Kernel
 * ============================================================================ */
float synapse_track_dist(float px, float py, float cx, float cy);

void synapse_car_cast_rays(
    float car_x,
    float car_y,
    float car_heading,
    float cx,
    float cy,
    float max_range,
    float half_width,
    float* out_ray_end_x,   /* [5] */
    float* out_ray_end_y,   /* [5] */
    float* out_norm_dist,   /* [5] in [0..1] */
    float* out_obs_inputs   /* [5] in [-1..1] */
);

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
    const float* prey_genes, /* [n_prey * 4] */
    int n_pred,
    float* pred_x,
    float* pred_y,
    float* pred_vx,
    float* pred_vy,
    float* pred_score,
    const float* pred_genes, /* [n_pred * 4] */
    int n_food,
    float* food_x,
    float* food_y,
    float width,
    float height,
    float vision_radius,
    float prey_speed,
    float pred_speed,
    unsigned int rng_seed
);

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
);

/* ============================================================================
 * 5. LAB 1: Rocket Moon Lander Physics, Shaping & Terrain Collision Kernel
 * ============================================================================ */
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
);

/* ============================================================================
 * 6. NEAT Feed-Forward Topological Evaluation Kernel
 * ============================================================================ */
void synapse_neat_forward(
    int num_nodes,
    const float* node_biases,
    float* node_acts,          /* pre-populated with inputs at 0..num_inputs-1 */
    int eval_start_idx,
    int num_conns,
    const int* conn_in_idx,
    const int* conn_out_idx,
    const float* conn_weights
);

/* ============================================================================
 * 7. BuildbitOS 1.58-Bit Ternary Bit-Sliced POPCNT & Mamba SSM Potato Kernels
 * ============================================================================ */
void synapse_trit64_bench(
    int dim,
    int n_tokens,
    float* out_fp32_ms,
    float* out_trit_ms,
    float* out_speedup,
    int* out_exact_match
);

void synapse_mamba_ssm_bench(
    int d_inner,
    int n_tokens,
    float* out_scan_ms,
    float* out_tok_per_sec,
    float* out_state_kb
);

#ifdef __cplusplus
}
#endif

#endif /* SYNAPSE_SIM_CORE_H */

