"""
Lab 1: NEAT Rocket Moon Lander Simulation
2D lunar physics engine + NEAT neuroevolution population.
"""

import math
import random
from typing import Dict, Any, List, Tuple
from workbench.labs.neat_core import NEATPopulation, NEATGenome


class RocketAgent:
    def __init__(self, genome: NEATGenome, start_x: float, start_y: float, fuel: float):
        self.genome = genome
        self.x = start_x + random.uniform(-35.0, 35.0)
        self.y = start_y + random.uniform(-10.0, 10.0)
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = 0.0
        self.angle = random.uniform(-0.18, 0.18)  # Radians (0 = upright)
        self.v_angle = 0.0
        self.fuel = fuel
        self.alive = True
        self.landed = False
        self.crashed = False
        self.left_thruster = False
        self.right_thruster = False
        self.main_thruster = False
        self.steps = 0
        self.prev_shaping: float = 0.0
        self.total_reward: float = 0.0


class NEATMoonLanderLab:
    """Interactive NEAT Moon Lander Lab with real-time variable controls."""

    VARIABLE_SPECS = [
        {"key": "gravity", "label": "Gravity (m/s²)", "desc": "Moon=1.62, Mars=3.72, Earth=9.8", "min": 0.4, "max": 9.8, "step": 0.1, "default": 1.62},
        {"key": "wind", "label": "Crosswind Force", "desc": "Horizontal wind turbulence pushing the rocket", "min": -1.5, "max": 1.5, "step": 0.05, "default": 0.0},
        {"key": "fuel_capacity", "label": "Fuel Capacity", "desc": "Total propellant units per rocket", "min": 50.0, "max": 300.0, "step": 10.0, "default": 150.0},
        {"key": "pop_size", "label": "Population Size", "desc": "Number of rockets per generation", "min": 20.0, "max": 160.0, "step": 10.0, "default": 60.0},
        {"key": "conn_add_prob", "label": "Add Synapse Rate", "desc": "Probability of evolving a new neural wire", "min": 0.02, "max": 0.50, "step": 0.02, "default": 0.18},
        {"key": "node_add_prob", "label": "Add Neuron Rate", "desc": "Probability of evolving a new hidden neuron", "min": 0.01, "max": 0.25, "step": 0.01, "default": 0.06},
        {"key": "weight_mutate_power", "label": "Mutation Power", "desc": "Strength of synaptic weight tweaks", "min": 0.10, "max": 1.50, "step": 0.05, "default": 0.60},
        {"key": "landing_bonus", "label": "Landing Reward", "desc": "Fitness bonus for soft upright touchdown on pad", "min": 50.0, "max": 400.0, "step": 10.0, "default": 240.0},
        {"key": "thruster_power", "label": "Main Thruster Power", "desc": "Engine thrust multiplier relative to gravity", "min": 1.10, "max": 2.60, "step": 0.10, "default": 1.65},
        {"key": "target_hidden", "label": "Hidden Neurons (+/-)", "desc": "Directly add or subtract hidden neurons in fleet brains", "min": 0.0, "max": 20.0, "step": 1.0, "default": 0.0},
    ]

    def __init__(self):
        self.width = 640.0
        self.height = 420.0
        self.pad_x = 320.0
        self.pad_y = 365.0
        self.pad_half_w = 52.0
        self.max_steps = 260

        self.params: Dict[str, float] = {s["key"]: s["default"] for s in self.VARIABLE_SPECS}
        self.terrain: List[Tuple[float, float]] = self._build_terrain()

        self.neat = NEATPopulation(
            num_inputs=8,
            num_outputs=4,
            pop_size=int(self.params["pop_size"]),
            conn_add_prob=self.params["conn_add_prob"],
            node_add_prob=self.params["node_add_prob"],
            weight_mutate_power=self.params["weight_mutate_power"]
        )
        self.rockets: List[RocketAgent] = []
        self.landed_count_last_gen = 0
        self.reset_generation()

    def _build_terrain(self) -> List[Tuple[float, float]]:
        pts = [
            (0.0, 330.0), (55.0, 355.0), (110.0, 315.0), (175.0, 360.0),
            (235.0, 345.0), (self.pad_x - self.pad_half_w, self.pad_y),
            (self.pad_x + self.pad_half_w, self.pad_y),
            (415.0, 340.0), (480.0, 362.0), (545.0, 318.0), (600.0, 350.0), (640.0, 335.0)
        ]
        return pts

    def modify_brain_structure(self, delta_neurons: int = 0, delta_synapses: int = 0) -> Dict[str, Any]:
        info = self.neat.modify_structure(delta_neurons=delta_neurons, delta_synapses=delta_synapses)
        self.params["target_hidden"] = float(info["hidden_nodes"])
        return info

    def update_param(self, key: str, value: float) -> None:
        old_val = self.params.get(key, 0.0)
        self.params[key] = float(value)
        if key == "target_hidden":
            cur_hidden = sum(1 for n in self.neat.best_genome.nodes.values() if n.type == "hidden")
            diff = int(round(value)) - cur_hidden
            if diff != 0:
                self.neat.modify_structure(delta_neurons=diff, delta_synapses=0)
        self.neat.conn_add_prob = self.params["conn_add_prob"]
        self.neat.node_add_prob = self.params["node_add_prob"]
        self.neat.weight_mutate_power = self.params["weight_mutate_power"]
        new_pop = int(self.params["pop_size"])
        if new_pop != self.neat.pop_size:
            self.neat.pop_size = new_pop

    def _compute_shaping(self, r: RocketAgent) -> float:
        dx = (r.x - self.pad_x) / (self.width * 0.5)
        dy = (self.pad_y - r.y) / self.height
        dist = math.sqrt(dx * dx + dy * dy)
        speed = math.sqrt(r.vx * r.vx + r.vy * r.vy) / 6.0
        tilt = abs(r.angle) / 1.2
        return -110.0 * dist - 45.0 * speed - 35.0 * tilt

    def reset_generation(self) -> None:
        self.rockets = []
        for g in self.neat.genomes:
            g.fitness = 0.0
            r = RocketAgent(g, start_x=self.pad_x, start_y=62.0, fuel=self.params["fuel_capacity"])
            r.prev_shaping = self._compute_shaping(r)
            self.rockets.append(r)

    def _terrain_height_at(self, x: float) -> float:
        x = max(0.0, min(self.width, x))
        for i in range(len(self.terrain) - 1):
            x1, y1 = self.terrain[i]
            x2, y2 = self.terrain[i + 1]
            if x1 <= x <= x2:
                t = (x - x1) / max(1e-5, x2 - x1)
                return y1 + t * (y2 - y1)
        return self.pad_y

    def step_physics(self) -> bool:
        """Advance all active rockets by 1 physics frame. Returns True if generation finished."""
        dt = 0.12
        g_acc = self.params["gravity"] * 0.45
        wind_acc = self.params["wind"] * 0.25
        active_any = False

        for r in self.rockets:
            if not r.alive:
                continue
            active_any = True
            r.steps += 1

            # 8 Normalized Sensor Inputs
            obs = [
                (r.x - self.pad_x) / 300.0,
                (self.pad_y - r.y) / 350.0,
                r.vx / 6.0,
                r.vy / 6.0,
                r.angle,
                r.v_angle * 2.0,
                1.0 if abs(r.x - self.pad_x) <= self.pad_half_w else -1.0,
                r.fuel / max(1.0, self.params["fuel_capacity"])
            ]
            out = r.genome.forward(obs)
            # Actions: 0=Idle, 1=Left Rotational, 2=Main Thruster, 3=Right Rotational
            r.main_thruster = (out[2] > 0.15) and (r.fuel > 0)
            r.left_thruster = (out[1] > out[3] + 0.15) and (r.fuel > 0)
            r.right_thruster = (out[3] > out[1] + 0.15) and (r.fuel > 0)

            ax = wind_acc
            ay = g_acc

            if r.main_thruster:
                thrust = self.params.get("thruster_power", 1.65) * max(0.7, g_acc)
                ax += math.sin(r.angle) * thrust
                ay -= math.cos(r.angle) * thrust
                r.fuel = max(0.0, r.fuel - 0.55)
                r.total_reward -= 0.04

            if r.left_thruster:
                r.v_angle += 0.045
                r.fuel = max(0.0, r.fuel - 0.15)
            elif r.right_thruster:
                r.v_angle -= 0.045
                r.fuel = max(0.0, r.fuel - 0.15)

            # Angular damping
            r.v_angle *= 0.92
            r.angle += r.v_angle
            r.vx += ax * dt
            r.vy += ay * dt
            r.x += r.vx
            r.y += r.vy

            # Potential-based shaping reward delta
            new_shaping = self._compute_shaping(r)
            r.total_reward += (new_shaping - r.prev_shaping) - 0.06  # Small time penalty prevents hovering
            r.prev_shaping = new_shaping

            # Check boundaries or ground contact
            ground_y = self._terrain_height_at(r.x)
            if r.x < 15.0 or r.x > self.width - 15.0 or r.y < 10.0:
                r.alive = False
                r.crashed = True
                r.total_reward -= 110.0
            elif r.y >= ground_y - 10.0:
                r.y = ground_y - 10.0
                r.alive = False
                on_pad = abs(r.x - self.pad_x) <= self.pad_half_w
                soft_speed = (abs(r.vx) < 1.65 and abs(r.vy) < 2.15)
                upright = abs(r.angle) < 0.35
                if on_pad and soft_speed and upright:
                    r.landed = True
                    r.total_reward += self.params["landing_bonus"] + (r.fuel * 0.25)
                else:
                    r.crashed = True
                    r.total_reward -= 75.0
            elif r.steps >= self.max_steps:
                r.alive = False
                r.total_reward -= 25.0

            r.genome.fitness = r.total_reward

        if not active_any:
            self.landed_count_last_gen = sum(1 for r in self.rockets if r.landed)
            self.neat.evolve_generation()
            self.reset_generation()
            return True
        return False

    def fast_forward_generations(self, num_gens: int = 25) -> Dict[str, Any]:
        """Run `num_gens` complete generations headlessly at turbo CPU speed."""
        completed = 0
        while completed < num_gens:
            if self.step_physics():
                completed += 1
        return self.get_telemetry()

    def get_leader(self) -> RocketAgent:
        alive = [r for r in self.rockets if r.alive]
        pool = alive if alive else self.rockets
        return max(pool, key=lambda r: r.total_reward)

    def get_telemetry(self) -> Dict[str, Any]:
        best_fit = self.neat.history_best[-1] if self.neat.history_best else 0.0
        avg_fit = self.neat.history_avg[-1] if self.neat.history_avg else 0.0
        return {
            "lab": "NEAT Rocket Moon Lander",
            "generation": self.neat.generation,
            "species": len(self.neat.species),
            "best_fitness": round(best_fit, 1),
            "avg_fitness": round(avg_fit, 1),
            "landed_last_gen": self.landed_count_last_gen,
            "best_ever": round(self.neat.best_fitness_ever, 1),
            "champion_nodes": len(self.neat.best_genome.nodes),
            "champion_synapses": sum(1 for c in self.neat.best_genome.connections.values() if c.enabled),
            "params": dict(self.params)
        }
