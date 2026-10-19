"""
SynapseOS Live Code Mirror & Standalone Python Script Generator.
Generates clean, runnable Python scripts dynamically reflecting the user's
current point-and-click slider variables across all AI labs.
"""

from typing import Dict, Any


def generate_lab_python_code(lab_id: str, params: Dict[str, float], telemetry: Dict[str, Any]) -> str:
    """Return a clean standalone Python experiment script with current slider variables injected."""
    if lab_id == "moon_lander":
        return f'''#!/usr/bin/env python3
"""
SynapseOS Auto-Generated Experiment: NEAT Rocket Moon Lander
Champion Fitness: {telemetry.get('best_ever', 0.0)} | Generation: {telemetry.get('generation', 1)}
"""

from workbench.labs.moon_lander import NEATMoonLanderLab

# --- 1. Point-and-Click Variables Selected in Synapse Studio ---
CONFIG = {{
    "gravity": {params.get("gravity", 1.62)},            # Lunar gravity (m/s^2)
    "wind": {params.get("wind", 0.0)},               # Crosswind force
    "fuel_capacity": {params.get("fuel_capacity", 150.0)},     # Propellant units
    "pop_size": {int(params.get("pop_size", 60))},            # Rockets per generation
    "conn_add_prob": {params.get("conn_add_prob", 0.18)},       # Synapse mutation probability
    "node_add_prob": {params.get("node_add_prob", 0.06)},       # Hidden neuron mutation probability
    "weight_mutate_power": {params.get("weight_mutate_power", 0.60)}, # Weight perturbation sigma
    "landing_bonus": {params.get("landing_bonus", 240.0)},       # Touchdown reward bonus
}}

if __name__ == "__main__":
    lab = NEATMoonLanderLab()
    for k, v in CONFIG.items():
        lab.update_param(k, v)
    lab.reset_generation()

    print("Evolving NEAT Moon Lander for 25 generations...")
    stats = lab.fast_forward_generations(25)
    print(f"Done! Best Fitness: {{stats['best_ever']}} | Nodes: {{stats['champion_nodes']}} | Synapses: {{stats['champion_synapses']}}")
'''

    if lab_id == "raycast_car":
        return f'''#!/usr/bin/env python3
"""
SynapseOS Auto-Generated Experiment: NEAT 5-Ray Lidar Self-Driving Car
Champion Fitness: {telemetry.get('best_ever', 0.0)} | Generation: {telemetry.get('generation', 1)}
"""

from workbench.labs.raycast_car import NEATRaycastCarLab

CONFIG = {{
    "sensor_range": {params.get("sensor_range", 125.0)},       # Laser raycast lookahead (px)
    "max_speed": {params.get("max_speed", 4.5)},            # Top forward velocity
    "turn_rate": {params.get("turn_rate", 0.09)},           # Steering agility (rad/frame)
    "track_width": {params.get("track_width", 40.0)},         # Road corridor half-width
    "pop_size": {int(params.get("pop_size", 40))},            # Cars per generation
    "conn_add_prob": {params.get("conn_add_prob", 0.16)},
    "node_add_prob": {params.get("node_add_prob", 0.05)},
    "weight_mutate_power": {params.get("weight_mutate_power", 0.55)},
}}

if __name__ == "__main__":
    lab = NEATRaycastCarLab()
    for k, v in CONFIG.items():
        lab.update_param(k, v)
    lab.reset_generation()

    stats = lab.fast_forward_generations(20)
    print(f"Self-Driving Evolution Complete! Best Score: {{stats['best_ever']}}")
'''

    if lab_id == "rl_gridworld":
        algo_name = "SARSA" if params.get("use_sarsa", 0.0) >= 0.5 else "Q-Learning"
        return f'''#!/usr/bin/env python3
"""
SynapseOS Auto-Generated Experiment: Tabular {algo_name} Hazard GridWorld
Episodes Trained: {telemetry.get('generation', 1)} | Goal Wins: {telemetry.get('species', 0)}
"""

from workbench.labs.rl_gridworld import RLGridWorldLab

# Bellman Update: Q(s,a) <- Q(s,a) + alpha * [r + gamma * max_a' Q(s',a') - Q(s,a)]
CONFIG = {{
    "alpha": {params.get("alpha", 0.25)},               # Learning rate
    "gamma": {params.get("gamma", 0.95)},               # Discount factor (foresight)
    "epsilon": {params.get("epsilon", 0.12)},             # Exploration rate
    "goal_reward": {params.get("goal_reward", 120.0)},        # Treasure reward
    "lava_penalty": {params.get("lava_penalty", -100.0)},      # Lava cliff penalty
    "step_penalty": {params.get("step_penalty", -1.0)},        # Step energy cost
    "wind_prob": {params.get("wind_prob", 0.05)},          # Stochastic wind chance
    "use_sarsa": {int(params.get("use_sarsa", 0.0))},              # 0=Q-Learning, 1=SARSA
}}

if __name__ == "__main__":
    lab = RLGridWorldLab()
    for k, v in CONFIG.items():
        lab.update_param(k, v)
    stats = lab.fast_forward_generations(100)
    print(f"Trained 100 RL episodes! Wins: {{stats['species']}} | Best Return: {{stats['best_ever']}}")
'''

    if lab_id == "cartpole_rl":
        return f'''#!/usr/bin/env python3
"""
SynapseOS Auto-Generated Experiment: CartPole & Inverted Pendulum Control
Best Balance Score: {telemetry.get('best_ever', 0.0)} | Generation: {telemetry.get('generation', 1)}
"""

from workbench.labs.cartpole_rl import CartPoleLab

CONFIG = {{
    "gravity": {params.get("gravity", 9.8)},
    "pole_length": {params.get("pole_length", 0.65)},
    "force_mag": {params.get("force_mag", 11.0)},
    "wind_gust": {params.get("wind_gust", 0.15)},
    "pop_size": {int(params.get("pop_size", 35))},
    "conn_add_prob": {params.get("conn_add_prob", 0.14)},
    "node_add_prob": {params.get("node_add_prob", 0.05)},
    "weight_mutate_power": {params.get("weight_mutate_power", 0.45)},
}}

if __name__ == "__main__":
    lab = CartPoleLab()
    for k, v in CONFIG.items():
        lab.update_param(k, v)
    lab.reset_generation()
    stats = lab.fast_forward_generations(25)
    print(f"CartPole Evolution Complete! Best Score: {{stats['best_ever']}}")
'''

    if lab_id == "nn_playground":
        return f'''#!/usr/bin/env python3
"""
SynapseOS Auto-Generated Experiment: Neural Network Backpropagation Playground
Classification Accuracy: {telemetry.get('best_fitness', 0.0)}% | Cross-Entropy Loss: {telemetry.get('avg_fitness', 0.0)}
"""

from workbench.labs.nn_playground import NeuralPlaygroundLab

CONFIG = {{
    "dataset_id": {int(params.get("dataset_id", 1))},          # 0=XOR, 1=Rings, 2=Moons, 3=Spiral
    "hidden_neurons": {int(params.get("hidden_neurons", 8))},      # Hidden layer width
    "learning_rate": {params.get("learning_rate", 0.18)},       # Gradient descent step size
    "l2_reg": {params.get("l2_reg", 0.001)},             # L2 weight decay
    "noise": {params.get("noise", 0.06)},               # Sample noise
}}

if __name__ == "__main__":
    lab = NeuralPlaygroundLab()
    for k, v in CONFIG.items():
        lab.update_param(k, v)
    stats = lab.fast_forward_generations(50)
    print(f"MLP Training Complete! Accuracy: {{stats['best_fitness']}}% | Loss: {{stats['avg_fitness']}}")
'''

    if lab_id == "prime_attention":
        return f'''#!/usr/bin/env python3
"""
Synapse Studio Auto-Generated Experiment: PRIME Moment Sliding-Window Attention
Combines a bounded Sliding Window (W) with O(D^2) 2nd-Order Taylor Moment Recurrence.
"""
from workbench.labs.prime_attention_lab import PrimeAttentionLab

CONFIG = {{
    "window_size": {int(params.get("window_size", 64))},
    "decay": {params.get("decay", 0.9990)},
    "alpha": {params.get("alpha", 0.45)},
    "head_dim": {int(params.get("head_dim", 32))},
    "use_qk_norm": {int(params.get("use_qk_norm", 1))},
    "distractor_gap": {int(params.get("distractor_gap", 256))},
}}

if __name__ == "__main__":
    lab = PrimeAttentionLab()
    for k, v in CONFIG.items():
        lab.update_param(k, v)
    stats = lab.fast_forward_generations(10)
    print(f"PRIME Sliding-Window Complete! Retention @ Gap={{CONFIG['distractor_gap']}}: {{stats['best_fitness']}}% (vs Linear ELU+1: {{stats['avg_fitness']}}%)")
    print(f"Constant O(1) State Memory: {{stats['state_kb']}} KB | C99 Throughput: {{stats['c_tokens_per_sec']}} tok/s")
'''

    # Swarm Ecosystem
    return f'''#!/usr/bin/env python3
"""
SynapseOS Auto-Generated Experiment: Co-Evolving Predator-Prey Swarm
Generation: {telemetry.get('generation', 1)} | Best Prey Fitness: {telemetry.get('best_ever', 0.0)}
"""

from workbench.labs.swarm_ecosystem import SwarmEcosystemLab

CONFIG = {{
    "num_prey": {int(params.get("num_prey", 35))},
    "num_predators": {int(params.get("num_predators", 4))},
    "vision_radius": {params.get("vision_radius", 85.0)},
    "prey_speed": {params.get("prey_speed", 4.0)},
    "predator_speed": {params.get("predator_speed", 4.2)},
    "food_count": {int(params.get("food_count", 28))},
    "mutation_sigma": {params.get("mutation_sigma", 0.20)},
}}

if __name__ == "__main__":
    lab = SwarmEcosystemLab()
    for k, v in CONFIG.items():
        lab.update_param(k, v)
    lab.reset_ecosystem()
    stats = lab.fast_forward_generations(15)
    print(f"Swarm Co-Evolution Complete! Top Prey Score: {{stats['best_ever']}} | Genes: {{stats.get('top_prey_genes')}}")
'''

