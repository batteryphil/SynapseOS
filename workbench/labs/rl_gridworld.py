"""
Lab 3: Reinforcement Learning (Tabular Q-Learning & SARSA Hazard GridWorld)
Visualizes real-time Bellman value iteration, Q(s, a) state-value heatmaps,
and optimal directional policy arrows across lava cliffs and treasure goals.
"""

import random
from typing import Dict, Any, List, Tuple


class RLGridWorldLab:
    VARIABLE_SPECS = [
        {"key": "alpha", "label": "Learning Rate (α)", "desc": "Step size for Bellman Q-table updates", "min": 0.02, "max": 0.90, "step": 0.02, "default": 0.25},
        {"key": "gamma", "label": "Discount Factor (γ)", "desc": "Foresight weight on future rewards", "min": 0.50, "max": 0.99, "step": 0.01, "default": 0.95},
        {"key": "epsilon", "label": "Exploration (ε)", "desc": "Probability of trying a random curious action", "min": 0.01, "max": 0.60, "step": 0.02, "default": 0.12},
        {"key": "goal_reward", "label": "Treasure Reward", "desc": "Positive reward upon reaching the gold goal", "min": 20.0, "max": 300.0, "step": 10.0, "default": 120.0},
        {"key": "lava_penalty", "label": "Lava Cliff Penalty", "desc": "Negative penalty for stepping into lava", "min": -250.0, "max": -20.0, "step": 10.0, "default": -100.0},
        {"key": "step_penalty", "label": "Step Cost", "desc": "Per-move energy cost (encourages shortest path)", "min": -5.0, "max": -0.1, "step": 0.1, "default": -1.0},
        {"key": "wind_prob", "label": "Wind Slip Chance", "desc": "Stochastic probability of being blown 1 cell up/down", "min": 0.0, "max": 0.35, "step": 0.05, "default": 0.05},
        {"key": "use_sarsa", "label": "Algorithm (0=Q, 1=SARSA)", "desc": "0: Off-policy Q-Learning, 1: On-policy SARSA", "min": 0.0, "max": 1.0, "step": 1.0, "default": 0.0},
        {"key": "max_ep_steps", "label": "Episode Horizon", "desc": "Max steps per episode before timeout", "min": 30.0, "max": 180.0, "step": 10.0, "default": 90.0},
    ]

    # Actions: 0=Up, 1=Right, 2=Down, 3=Left
    DELTAS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    ARROWS = ["↑", "→", "↓", "←"]

    def __init__(self):
        self.cols = 10
        self.rows = 7
        self.start_pos = (0, 6)
        self.goal_pos = (9, 6)
        self.params: Dict[str, float] = {s["key"]: s["default"] for s in self.VARIABLE_SPECS}

        # Lava cliff along bottom row + internal obstacles
        self.lava_cells = {(2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (4, 2), (5, 2)}
        self.wall_cells = {(2, 3), (2, 4), (7, 2), (7, 3)}

        self.q_table: Dict[Tuple[int, int], List[float]] = {}
        self.episode = 1
        self.wins = 0
        self.history_best: List[float] = []
        self.history_avg: List[float] = []
        self.recent_returns: List[float] = []
        self.agent_pos = self.start_pos
        self.trail: List[Tuple[int, int]] = [self.start_pos]
        self.current_return = 0.0
        self.steps_in_ep = 0
        self.reset_q_table()

    def modify_brain_structure(self, delta_neurons: int = 0, delta_synapses: int = 0) -> Dict[str, Any]:
        # Adjust discount foresight / learning rate and return Q-state capacity
        if delta_neurons != 0:
            self.params["gamma"] = max(0.50, min(0.99, self.params["gamma"] + delta_neurons * 0.02))
        if delta_synapses != 0:
            self.params["alpha"] = max(0.02, min(0.90, self.params["alpha"] + delta_synapses * 0.05))
        return {
            "total_nodes": self.cols * self.rows,
            "hidden_nodes": len(self.q_table),
            "enabled_synapses": len(self.q_table) * 4,
        }

    def reset_q_table(self) -> None:
        self.q_table = {
            (c, r): [0.0, 0.0, 0.0, 0.0]
            for c in range(self.cols)
            for r in range(self.rows)
        }
        self.episode = 1
        self.wins = 0
        self.history_best = []
        self.history_avg = []
        self.recent_returns = []
        self.reset_episode()

    def reset_episode(self) -> None:
        self.agent_pos = self.start_pos
        self.trail = [self.start_pos]
        self.current_return = 0.0
        self.steps_in_ep = 0

    def update_param(self, key: str, value: float) -> None:
        self.params[key] = float(value)

    def choose_action(self, state: Tuple[int, int]) -> int:
        if random.random() < self.params["epsilon"]:
            return random.randint(0, 3)
        q_vals = self.q_table[state]
        max_q = max(q_vals)
        best_actions = [i for i, q in enumerate(q_vals) if abs(q - max_q) < 1e-6]
        return random.choice(best_actions)

    def step_physics(self) -> bool:
        """Execute 1 RL step (and update Q-table). Returns True if episode completed."""
        s = self.agent_pos
        a = self.choose_action(s)

        dx, dy = self.DELTAS[a]
        nx, ny = s[0] + dx, s[1] + dy

        # Optional stochastic wind
        if random.random() < self.params["wind_prob"]:
            ny += random.choice([-1, 1])

        nx = max(0, min(self.cols - 1, nx))
        ny = max(0, min(self.rows - 1, ny))
        if (nx, ny) in self.wall_cells:
            nx, ny = s

        next_s = (nx, ny)
        done = False

        if next_s == self.goal_pos:
            reward = self.params["goal_reward"]
            done = True
            self.wins += 1
        elif next_s in self.lava_cells:
            reward = self.params["lava_penalty"]
            done = True
        else:
            reward = self.params["step_penalty"]

        self.steps_in_ep += 1
        if self.steps_in_ep >= 90:
            done = True

        # Bellman Update (Q-Learning vs SARSA)
        alpha = self.params["alpha"]
        gamma = self.params["gamma"]
        q_sa = self.q_table[s][a]

        if done:
            target = reward
        elif self.params["use_sarsa"] >= 0.5:
            next_a = self.choose_action(next_s)
            target = reward + gamma * self.q_table[next_s][next_a]
        else:
            target = reward + gamma * max(self.q_table[next_s])

        self.q_table[s][a] = q_sa + alpha * (target - q_sa)

        self.agent_pos = next_s
        self.trail.append(next_s)
        self.current_return += reward

        if done:
            self.episode += 1
            self.recent_returns.append(self.current_return)
            if len(self.recent_returns) > 30:
                self.recent_returns.pop(0)
            avg_r = sum(self.recent_returns) / len(self.recent_returns)
            best_r = max(self.recent_returns)
            self.history_best.append(round(best_r, 1))
            self.history_avg.append(round(avg_r, 1))
            self.reset_episode()
            return True
        return False

    def fast_forward_generations(self, num_gens: int = 50) -> Dict[str, Any]:
        completed = 0
        while completed < num_gens:
            if self.step_physics():
                completed += 1
        return self.get_telemetry()

    def get_telemetry(self) -> Dict[str, Any]:
        algo = "SARSA (On-Policy)" if self.params["use_sarsa"] >= 0.5 else "Q-Learning (Off-Policy)"
        best_r = self.history_best[-1] if self.history_best else 0.0
        avg_r = self.history_avg[-1] if self.history_avg else 0.0
        return {
            "lab": f"RL GridWorld ({algo})",
            "generation": self.episode,
            "species": self.wins,
            "best_fitness": round(best_r, 1),
            "avg_fitness": round(avg_r, 1),
            "best_ever": round(max(self.history_best) if self.history_best else 0.0, 1),
            "params": dict(self.params)
        }
