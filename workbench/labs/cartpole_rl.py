"""
Lab 4: CartPole & Inverted Pendulum Control (Neuro-Policy / RL)
Balances an unstable inverted pole on a motorized cart subject to gravity and wind gusts.
"""

import math
import random
from typing import Dict, Any, List
from workbench.labs.neat_core import NEATPopulation, NEATGenome


class CartPoleAgent:
    def __init__(self, genome: NEATGenome):
        self.genome = genome
        self.x = random.uniform(-0.2, 0.2)      # Cart position [-2.4 .. +2.4 m]
        self.vx = 0.0
        self.theta = random.uniform(-0.08, 0.08) # Pole angle (0 = upright)
        self.v_theta = 0.0
        self.alive = True
        self.steps = 0
        self.fitness = 0.0
        self.last_force = 0.0


class CartPoleLab:
    VARIABLE_SPECS = [
        {"key": "gravity", "label": "Gravity (m/s²)", "desc": "Downward gravitational acceleration", "min": 1.6, "max": 22.0, "step": 0.5, "default": 9.8},
        {"key": "pole_length", "label": "Pole Length (m)", "desc": "Half-length of the balanced pole", "min": 0.25, "max": 1.80, "step": 0.05, "default": 0.65},
        {"key": "force_mag", "label": "Motor Force (N)", "desc": "Horizontal cart motor thrust", "min": 4.0, "max": 25.0, "step": 1.0, "default": 11.0},
        {"key": "wind_gust", "label": "Random Wind Disturbance", "desc": "Random torque buffeting the pole", "min": 0.0, "max": 2.5, "step": 0.1, "default": 0.15},
        {"key": "pop_size", "label": "Policy Population", "desc": "Number of candidate controllers per epoch", "min": 15.0, "max": 100.0, "step": 5.0, "default": 35.0},
        {"key": "conn_add_prob", "label": "Add Synapse Rate", "desc": "Probability of growing a new synapse", "min": 0.02, "max": 0.40, "step": 0.02, "default": 0.14},
        {"key": "node_add_prob", "label": "Add Neuron Rate", "desc": "Probability of adding a hidden neuron", "min": 0.01, "max": 0.25, "step": 0.01, "default": 0.05},
        {"key": "weight_mutate_power", "label": "Mutation Power", "desc": "Policy weight exploration step", "min": 0.05, "max": 1.20, "step": 0.05, "default": 0.45},
    ]

    def __init__(self):
        self.max_steps = 350
        self.x_threshold = 2.4
        self.theta_threshold = 0.42  # ~24 degrees
        self.params: Dict[str, float] = {s["key"]: s["default"] for s in self.VARIABLE_SPECS}

        self.neat = NEATPopulation(
            num_inputs=4,
            num_outputs=1,
            pop_size=int(self.params["pop_size"]),
            conn_add_prob=self.params["conn_add_prob"],
            node_add_prob=self.params["node_add_prob"],
            weight_mutate_power=self.params["weight_mutate_power"]
        )
        self.agents: List[CartPoleAgent] = []
        self.reset_generation()

    def update_param(self, key: str, value: float) -> None:
        self.params[key] = float(value)
        self.neat.conn_add_prob = self.params["conn_add_prob"]
        self.neat.node_add_prob = self.params["node_add_prob"]
        self.neat.weight_mutate_power = self.params["weight_mutate_power"]
        new_pop = int(self.params["pop_size"])
        if new_pop != self.neat.pop_size:
            self.neat.pop_size = new_pop

    def reset_generation(self) -> None:
        self.agents = []
        for g in self.neat.genomes:
            g.fitness = 0.0
            self.agents.append(CartPoleAgent(g))

    def step_physics(self) -> bool:
        dt = 0.02
        mass_cart = 1.0
        mass_pole = 0.1
        total_mass = mass_cart + mass_pole
        length = self.params["pole_length"]
        polemass_length = mass_pole * length
        g = self.params["gravity"]
        force_mag = self.params["force_mag"]
        wind = self.params["wind_gust"]

        active_any = False
        for ag in self.agents:
            if not ag.alive:
                continue
            active_any = True
            ag.steps += 1

            obs = [
                ag.x / self.x_threshold,
                ag.vx / 3.0,
                ag.theta / self.theta_threshold,
                ag.v_theta / 3.0
            ]
            out = ag.genome.forward(obs)
            force = out[0] * force_mag
            if wind > 0.0:
                force += random.gauss(0.0, wind)
            ag.last_force = force

            cos_t = math.cos(ag.theta)
            sin_t = math.sin(ag.theta)
            temp = (force + polemass_length * ag.v_theta * ag.v_theta * sin_t) / total_mass
            theta_acc = (g * sin_t - cos_t * temp) / (length * (4.0 / 3.0 - mass_pole * cos_t * cos_t / total_mass))
            x_acc = temp - polemass_length * theta_acc * cos_t / total_mass

            ag.x += dt * ag.vx
            ag.vx += dt * x_acc
            ag.theta += dt * ag.v_theta
            ag.v_theta += dt * theta_acc

            # Reward staying upright and centered
            center_bonus = 1.0 - (abs(ag.x) / self.x_threshold) * 0.5
            upright_bonus = 1.0 - (abs(ag.theta) / self.theta_threshold) * 0.7
            ag.fitness += center_bonus + upright_bonus

            if abs(ag.x) > self.x_threshold or abs(ag.theta) > self.theta_threshold or ag.steps >= self.max_steps:
                ag.alive = False

            ag.genome.fitness = ag.fitness

        if not active_any:
            self.neat.evolve_generation()
            self.reset_generation()
            return True
        return False

    def fast_forward_generations(self, num_gens: int = 25) -> Dict[str, Any]:
        completed = 0
        while completed < num_gens:
            if self.step_physics():
                completed += 1
        return self.get_telemetry()

    def get_leader(self) -> CartPoleAgent:
        alive = [a for a in self.agents if a.alive]
        pool = alive if alive else self.agents
        return max(pool, key=lambda a: a.fitness)

    def get_telemetry(self) -> Dict[str, Any]:
        best_fit = self.neat.history_best[-1] if self.neat.history_best else 0.0
        avg_fit = self.neat.history_avg[-1] if self.neat.history_avg else 0.0
        return {
            "lab": "CartPole Inverted Pendulum",
            "generation": self.neat.generation,
            "species": len(self.neat.species),
            "best_fitness": round(best_fit, 1),
            "avg_fitness": round(avg_fit, 1),
            "best_ever": round(self.neat.best_fitness_ever, 1),
            "champion_nodes": len(self.neat.best_genome.nodes),
            "champion_synapses": sum(1 for c in self.neat.best_genome.connections.values() if c.enabled),
            "params": dict(self.params)
        }
