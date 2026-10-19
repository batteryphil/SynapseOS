"""
Lab 2: NEAT Autonomous Self-Driving Car (5-Ray Lidar Circuit)
Cars use 5 laser distance raycasts + velocity sensor to evolve steering and throttle
control around a closed circuit track without colliding with track boundaries.
"""

import math
import random
from typing import Dict, Any, List, Tuple
from workbench.labs.neat_core import NEATPopulation, NEATGenome


class CarAgent:
    def __init__(self, genome: NEATGenome, start_x: float, start_y: float, start_heading: float):
        self.genome = genome
        self.x = start_x
        self.y = start_y
        self.heading = start_heading + random.uniform(-0.08, 0.08)
        self.speed = 2.0
        self.alive = True
        self.steps = 0
        self.distance_traveled = 0.0
        self.checkpoints_passed = 0
        self.next_cp_idx = 1
        self.rays: List[Tuple[float, float, float]] = []  # (end_x, end_y, normalized_dist)


class NEATRaycastCarLab:
    VARIABLE_SPECS = [
        {"key": "sensor_range", "label": "Lidar Ray Range (px)", "desc": "Max laser distance lookahead", "min": 50.0, "max": 220.0, "step": 10.0, "default": 125.0},
        {"key": "max_speed", "label": "Max Car Speed", "desc": "Top forward velocity per frame", "min": 2.0, "max": 8.0, "step": 0.5, "default": 4.5},
        {"key": "turn_rate", "label": "Steering Agility", "desc": "Max angular steering radians/frame", "min": 0.03, "max": 0.16, "step": 0.01, "default": 0.09},
        {"key": "track_width", "label": "Track Lane Width", "desc": "Half-width of road corridor (smaller = harder)", "min": 26.0, "max": 58.0, "step": 2.0, "default": 40.0},
        {"key": "pop_size", "label": "Population Size", "desc": "Number of cars per generation", "min": 20.0, "max": 120.0, "step": 10.0, "default": 40.0},
        {"key": "conn_add_prob", "label": "Add Synapse Rate", "desc": "Probability of adding a new neural connection", "min": 0.02, "max": 0.45, "step": 0.02, "default": 0.16},
        {"key": "node_add_prob", "label": "Add Neuron Rate", "desc": "Probability of splitting a synapse with a neuron", "min": 0.01, "max": 0.25, "step": 0.01, "default": 0.05},
        {"key": "weight_mutate_power", "label": "Mutation Power", "desc": "Magnitude of weight perturbations", "min": 0.10, "max": 1.50, "step": 0.05, "default": 0.55},
        {"key": "target_hidden", "label": "Hidden Neurons (+/-)", "desc": "Directly add or subtract hidden neurons in car brains", "min": 0.0, "max": 20.0, "step": 1.0, "default": 0.0},
    ]

    RAY_ANGLES = [-1.05, -0.52, 0.0, 0.52, 1.05]  # -60, -30, 0, +30, +60 deg

    def __init__(self):
        self.width = 640.0
        self.height = 420.0
        self.cx = 320.0
        self.cy = 210.0
        self.max_steps = 320
        self.params: Dict[str, float] = {s["key"]: s["default"] for s in self.VARIABLE_SPECS}

        self.num_waypoints = 24
        self.waypoints: List[Tuple[float, float]] = self._build_waypoints()

        # 6 inputs: 5 lidar rays + current speed; 2 outputs: steering, throttle
        self.neat = NEATPopulation(
            num_inputs=6,
            num_outputs=2,
            pop_size=int(self.params["pop_size"]),
            conn_add_prob=self.params["conn_add_prob"],
            node_add_prob=self.params["node_add_prob"],
            weight_mutate_power=self.params["weight_mutate_power"]
        )
        self.cars: List[CarAgent] = []
        self.reset_generation()

    def _build_waypoints(self) -> List[Tuple[float, float]]:
        pts = []
        for i in range(self.num_waypoints):
            theta = (2.0 * math.pi * i) / self.num_waypoints
            # Kidney / figure-oval circuit shape
            rx = 220.0 + 35.0 * math.cos(2.0 * theta)
            ry = 135.0 + 25.0 * math.sin(3.0 * theta)
            x = self.cx + rx * math.cos(theta)
            y = self.cy + ry * math.sin(theta)
            pts.append((x, y))
        return pts

    def modify_brain_structure(self, delta_neurons: int = 0, delta_synapses: int = 0) -> Dict[str, Any]:
        info = self.neat.modify_structure(delta_neurons=delta_neurons, delta_synapses=delta_synapses)
        self.params["target_hidden"] = float(info["hidden_nodes"])
        return info

    def update_param(self, key: str, value: float) -> None:
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

    def _dist_to_track_centerline(self, px: float, py: float) -> float:
        """O(1) analytical distance from point (px, py) to the parametric circuit centerline."""
        dx = px - self.cx
        dy = py - self.cy
        theta = math.atan2(dy, dx)
        rx = 220.0 + 35.0 * math.cos(2.0 * theta)
        ry = 135.0 + 25.0 * math.sin(3.0 * theta)
        tx = self.cx + rx * math.cos(theta)
        ty = self.cy + ry * math.sin(theta)
        return math.hypot(px - tx, py - ty)

    def _cast_rays(self, car: CarAgent) -> List[float]:
        max_r = self.params["sensor_range"]
        half_w = self.params["track_width"]
        car.rays = []
        norm_dists: List[float] = []

        for rel_ang in self.RAY_ANGLES:
            ang = car.heading + rel_ang
            ca, sa = math.cos(ang), math.sin(ang)
            dist = 0.0
            step = 10.0
            while dist < max_r:
                dist += step
                rx = car.x + ca * dist
                ry = car.y + sa * dist
                if self._dist_to_track_centerline(rx, ry) > half_w:
                    break
            rx = car.x + ca * dist
            ry = car.y + sa * dist
            nd = min(1.0, dist / max_r)
            car.rays.append((rx, ry, nd))
            norm_dists.append(nd * 2.0 - 1.0)
        return norm_dists

    def reset_generation(self) -> None:
        x0, y0 = self.waypoints[0]
        x1, y1 = self.waypoints[1]
        start_heading = math.atan2(y1 - y0, x1 - x0)
        self.cars = []
        for g in self.neat.genomes:
            g.fitness = 0.0
            c = CarAgent(g, x0, y0, start_heading)
            self._cast_rays(c)
            self.cars.append(c)

    def step_physics(self) -> bool:
        half_w = self.params["track_width"]
        max_spd = self.params["max_speed"]
        turn_r = self.params["turn_rate"]
        active_any = False

        for car in self.cars:
            if not car.alive:
                continue
            active_any = True
            car.steps += 1

            ray_inputs = self._cast_rays(car)
            obs = ray_inputs + [car.speed / max_spd]
            out = car.genome.forward(obs)

            steer = out[0] * turn_r
            throttle = (out[1] + 1.0) * 0.5  # [0..1]
            car.heading += steer
            car.speed = max(1.2, min(max_spd, car.speed * 0.9 + throttle * max_spd * 0.2))

            car.x += math.cos(car.heading) * car.speed
            car.y += math.sin(car.heading) * car.speed
            car.distance_traveled += car.speed

            # Check waypoint gate advancement
            wx, wy = self.waypoints[car.next_cp_idx]
            if math.hypot(car.x - wx, car.y - wy) < half_w * 1.15:
                car.checkpoints_passed += 1
                car.next_cp_idx = (car.next_cp_idx + 1) % self.num_waypoints

            # Check track off-road collision
            if self._dist_to_track_centerline(car.x, car.y) > half_w:
                car.alive = False

            if car.steps >= self.max_steps:
                car.alive = False

            car.genome.fitness = (car.checkpoints_passed * 35.0) + (car.distance_traveled * 0.15)

        if not active_any:
            self.neat.evolve_generation()
            self.reset_generation()
            return True
        return False

    def fast_forward_generations(self, num_gens: int = 20) -> Dict[str, Any]:
        completed = 0
        while completed < num_gens:
            if self.step_physics():
                completed += 1
        return self.get_telemetry()

    def get_leader(self) -> CarAgent:
        alive = [c for c in self.cars if c.alive]
        pool = alive if alive else self.cars
        return max(pool, key=lambda c: c.genome.fitness)

    def get_telemetry(self) -> Dict[str, Any]:
        best_fit = self.neat.history_best[-1] if self.neat.history_best else 0.0
        avg_fit = self.neat.history_avg[-1] if self.neat.history_avg else 0.0
        return {
            "lab": "NEAT Self-Driving Lidar Car",
            "generation": self.neat.generation,
            "species": len(self.neat.species),
            "best_fitness": round(best_fit, 1),
            "avg_fitness": round(avg_fit, 1),
            "best_ever": round(self.neat.best_fitness_ever, 1),
            "champion_nodes": len(self.neat.best_genome.nodes),
            "champion_synapses": sum(1 for c in self.neat.best_genome.connections.values() if c.enabled),
            "params": dict(self.params)
        }
