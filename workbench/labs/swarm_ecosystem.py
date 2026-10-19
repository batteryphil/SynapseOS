"""
Lab 6: Co-Evolving Predator-Prey Swarm Intelligence & Genetic Boids
Prey agents evolve sensory weights for food foraging, flock cohesion, and predator
evasion, while Predators evolve pursuit and interception behaviors.
"""

import math
import random
from typing import Dict, Any, List, Tuple


class SwarmAgent:
    def __init__(self, x: float, y: float, is_predator: bool = False):
        self.x = x
        self.y = y
        ang = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(ang) * 2.5
        self.vy = math.sin(ang) * 2.5
        self.is_predator = is_predator
        self.energy = 100.0
        self.score = 0.0
        # 4 genetic weights: [food_or_prey_attraction, predator_evasion, cohesion, separation]
        self.genes = [
            random.uniform(0.6, 1.8),
            random.uniform(1.0, 2.5),
            random.uniform(0.2, 1.0),
            random.uniform(0.5, 1.5)
        ]


class SwarmEcosystemLab:
    VARIABLE_SPECS = [
        {"key": "num_prey", "label": "Prey Flock Size", "desc": "Number of foraging prey agents", "min": 15.0, "max": 80.0, "step": 5.0, "default": 35.0},
        {"key": "num_predators", "label": "Predator Count", "desc": "Number of hunting predators", "min": 1.0, "max": 12.0, "step": 1.0, "default": 4.0},
        {"key": "vision_radius", "label": "Sensory Vision (px)", "desc": "Detection radius for threats and food", "min": 35.0, "max": 160.0, "step": 5.0, "default": 85.0},
        {"key": "prey_speed", "label": "Max Prey Speed", "desc": "Top evasion speed of prey", "min": 2.0, "max": 6.5, "step": 0.2, "default": 4.0},
        {"key": "predator_speed", "label": "Max Predator Speed", "desc": "Top pursuit speed of predators", "min": 2.0, "max": 6.5, "step": 0.2, "default": 4.2},
        {"key": "food_count", "label": "Food Resource Density", "desc": "Number of regenerating energy nodes", "min": 10.0, "max": 60.0, "step": 5.0, "default": 28.0},
        {"key": "mutation_sigma", "label": "Genetic Mutation Rate", "desc": "Offspring behavioral weight variation", "min": 0.05, "max": 0.60, "step": 0.05, "default": 0.20},
    ]

    def __init__(self):
        self.width = 640.0
        self.height = 420.0
        self.params: Dict[str, float] = {s["key"]: s["default"] for s in self.VARIABLE_SPECS}
        self.generation = 1
        self.step_counter = 0
        self.epoch_length = 220
        self.history_best: List[float] = []
        self.history_avg: List[float] = []
        self.prey: List[SwarmAgent] = []
        self.predators: List[SwarmAgent] = []
        self.foods: List[Tuple[float, float]] = []
        self.reset_ecosystem()

    def reset_ecosystem(self) -> None:
        n_prey = int(self.params["num_prey"])
        n_pred = int(self.params["num_predators"])
        n_food = int(self.params["food_count"])

        self.prey = [
            SwarmAgent(random.uniform(40, self.width - 40), random.uniform(40, self.height - 40), False)
            for _ in range(n_prey)
        ]
        self.predators = [
            SwarmAgent(random.uniform(40, self.width - 40), random.uniform(40, self.height - 40), True)
            for _ in range(n_pred)
        ]
        self.foods = [
            (random.uniform(25, self.width - 25), random.uniform(25, self.height - 25))
            for _ in range(n_food)
        ]
        self.step_counter = 0

    def update_param(self, key: str, value: float) -> None:
        self.params[key] = float(value)

    def step_physics(self) -> bool:
        vis = self.params["vision_radius"]
        prey_spd = self.params["prey_speed"]
        pred_spd = self.params["predator_speed"]
        self.step_counter += 1

        # Update Prey
        for p in self.prey:
            fx, fy = 0.0, 0.0
            # 1. Nearest food attraction
            if self.foods:
                nf = min(self.foods, key=lambda f: (f[0] - p.x) ** 2 + (f[1] - p.y) ** 2)
                d = math.hypot(nf[0] - p.x, nf[1] - p.y)
                if 1e-3 < d < vis * 1.4:
                    fx += ((nf[0] - p.x) / d) * p.genes[0]
                    fy += ((nf[1] - p.y) / d) * p.genes[0]
                if d < 10.0:
                    p.score += 15.0
                    p.energy = min(150.0, p.energy + 25.0)
                    idx = self.foods.index(nf)
                    self.foods[idx] = (random.uniform(25, self.width - 25), random.uniform(25, self.height - 25))

            # 2. Predator evasion
            for pred in self.predators:
                d = math.hypot(pred.x - p.x, pred.y - p.y)
                if 1e-3 < d < vis:
                    weight = (vis / d) * p.genes[1]
                    fx -= ((pred.x - p.x) / d) * weight
                    fy -= ((pred.y - p.y) / d) * weight

            # 3. Flock separation & cohesion
            for other in self.prey:
                if other is p:
                    continue
                d = math.hypot(other.x - p.x, other.y - p.y)
                if 1e-3 < d < 22.0:
                    fx -= ((other.x - p.x) / d) * p.genes[3]
                    fy -= ((other.y - p.y) / d) * p.genes[3]
                elif 22.0 <= d < vis * 0.7:
                    fx += ((other.x - p.x) / d) * (p.genes[2] * 0.15)
                    fy += ((other.y - p.y) / d) * (p.genes[2] * 0.15)

            # Soft wall repulsion
            margin = 35.0
            if p.x < margin:
                fx += 1.5
            elif p.x > self.width - margin:
                fx -= 1.5
            if p.y < margin:
                fy += 1.5
            elif p.y > self.height - margin:
                fy -= 1.5

            p.vx = p.vx * 0.85 + fx * 0.45
            p.vy = p.vy * 0.85 + fy * 0.45
            spd = math.hypot(p.vx, p.vy)
            if spd > prey_spd:
                p.vx = (p.vx / spd) * prey_spd
                p.vy = (p.vy / spd) * prey_spd
            p.x = max(8.0, min(self.width - 8.0, p.x + p.vx))
            p.y = max(8.0, min(self.height - 8.0, p.y + p.vy))
            p.score += 0.1

        # Update Predators
        for pred in self.predators:
            fx, fy = 0.0, 0.0
            if self.prey:
                target = min(self.prey, key=lambda p: (p.x - pred.x) ** 2 + (p.y - pred.y) ** 2)
                d = math.hypot(target.x - pred.x, target.y - pred.y)
                if d > 1e-3:
                    fx += ((target.x - pred.x) / d) * pred.genes[0]
                    fy += ((target.y - pred.y) / d) * pred.genes[0]
                if d < 11.0:
                    pred.score += 25.0
                    target.score = max(0.0, target.score - 12.0)
                    target.x = random.uniform(40, self.width - 40)
                    target.y = random.uniform(40, self.height - 40)

            pred.vx = pred.vx * 0.88 + fx * 0.42
            pred.vy = pred.vy * 0.88 + fy * 0.42
            spd = math.hypot(pred.vx, pred.vy)
            if spd > pred_spd:
                pred.vx = (pred.vx / spd) * pred_spd
                pred.vy = (pred.vy / spd) * pred_spd
            pred.x = max(8.0, min(self.width - 8.0, pred.x + pred.vx))
            pred.y = max(8.0, min(self.height - 8.0, pred.y + pred.vy))

        if self.step_counter >= self.epoch_length:
            self._evolve_swarm()
            return True
        return False

    def _evolve_swarm(self) -> None:
        self.prey.sort(key=lambda p: p.score, reverse=True)
        best_s = self.prey[0].score if self.prey else 0.0
        avg_s = sum(p.score for p in self.prey) / max(1, len(self.prey))
        self.history_best.append(round(best_s, 1))
        self.history_avg.append(round(avg_s, 1))

        sigma = self.params["mutation_sigma"]
        n_prey = int(self.params["num_prey"])
        elites = self.prey[:max(2, len(self.prey) // 4)]

        new_prey: List[SwarmAgent] = []
        for i in range(n_prey):
            parent = elites[i] if i < len(elites) else random.choice(elites)
            child = SwarmAgent(random.uniform(40, self.width - 40), random.uniform(40, self.height - 40), False)
            child.genes = [max(0.05, g + random.gauss(0.0, sigma if i >= len(elites) else 0.0)) for g in parent.genes]
            new_prey.append(child)

        self.prey = new_prey
        self.step_counter = 0
        self.generation += 1

    def fast_forward_generations(self, num_gens: int = 15) -> Dict[str, Any]:
        completed = 0
        while completed < num_gens:
            if self.step_physics():
                completed += 1
        return self.get_telemetry()

    def get_telemetry(self) -> Dict[str, Any]:
        best_fit = self.history_best[-1] if self.history_best else 0.0
        avg_fit = self.history_avg[-1] if self.history_avg else 0.0
        top_genes = [round(g, 2) for g in self.prey[0].genes] if self.prey else []
        return {
            "lab": "Co-Evolving Predator-Prey Swarm",
            "generation": self.generation,
            "species": len(self.prey),
            "best_fitness": round(best_fit, 1),
            "avg_fitness": round(avg_fit, 1),
            "best_ever": round(max(self.history_best) if self.history_best else 0.0, 1),
            "top_prey_genes": top_genes,
            "params": dict(self.params)
        }
