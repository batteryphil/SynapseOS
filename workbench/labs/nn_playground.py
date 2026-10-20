"""
Lab 5: Interactive Neural Network & 2D Decision Boundary Playground (Backprop MLP)
Trains a 2-layer Multi-Layer Perceptron via analytical backpropagation on non-linear
2D classification datasets (XOR, Concentric Rings, Two Moons, Spiral) at 60 FPS on CPU.
Features live dynamic dataset motion so the 2D decision boundary continuously adapts!
"""

import math
import random
from typing import Dict, Any, List, Tuple


class NeuralPlaygroundLab:
    VARIABLE_SPECS = [
        {"key": "dataset_id", "label": "Dataset (0=XOR,1=Ring,2=Moon,3=Spiral)", "desc": "Non-linear 2D classification geometry", "min": 0.0, "max": 3.0, "step": 1.0, "default": 2.0},
        {"key": "hidden_neurons", "label": "Hidden Layer Neurons (+/-)", "desc": "Capacity of the hidden representation layer", "min": 1.0, "max": 24.0, "step": 1.0, "default": 8.0},
        {"key": "learning_rate", "label": "Learning Rate (η)", "desc": "Gradient descent step size", "min": 0.01, "max": 0.60, "step": 0.02, "default": 0.22},
        {"key": "l2_reg", "label": "L2 Regularization (λ)", "desc": "Weight decay penalty preventing overfitting", "min": 0.0, "max": 0.02, "step": 0.001, "default": 0.001},
        {"key": "noise", "label": "Dataset Noise", "desc": "Gaussian jitter on sample coordinates", "min": 0.0, "max": 0.35, "step": 0.02, "default": 0.05},
        {"key": "steps_per_frame", "label": "Epochs per Frame", "desc": "Backprop gradient updates per render tick", "min": 1.0, "max": 20.0, "step": 1.0, "default": 4.0},
        {"key": "activation_gain", "label": "Activation Steepness", "desc": "Sharpness of Tanh non-linear boundary", "min": 0.5, "max": 3.0, "step": 0.1, "default": 1.2},
        {"key": "synapse_density", "label": "Active Input Features (2..4)", "desc": "2=Linear (x,y) only, 4=Full Polynomial (+r^2, x*y)", "min": 2.0, "max": 4.0, "step": 1.0, "default": 4.0},
    ]

    DATASET_NAMES = {0: "XOR Checkerboard", 1: "Concentric Rings", 2: "Two Interleaving Moons", 3: "Archimedean Spiral"}

    def __init__(self):
        self.params: Dict[str, float] = {s["key"]: s["default"] for s in self.VARIABLE_SPECS}
        self.base_samples: List[Tuple[float, float, float]] = []
        self.samples: List[Tuple[float, float, float]] = []  # (x in [-1,1], y in [-1,1], label in {0, 1})
        self.epoch = 0
        self.loss = 0.693
        self.accuracy = 50.0
        self.swirl_phase = 0.0
        self.history_best: List[float] = []  # Accuracy %
        self.history_avg: List[float] = []   # Scaled (1 - loss) * 100

        self.w1: List[List[float]] = []  # [hidden][4 features: x, y, x^2+y^2, x*y]
        self.b1: List[float] = []
        self.w2: List[float] = []        # [hidden]
        self.b2: float = 0.0

        self.rebuild_dataset()
        self.rebuild_network()

    def modify_brain_structure(self, delta_neurons: int = 0, delta_synapses: int = 0) -> Dict[str, Any]:
        """Dynamically add or remove hidden neurons without wiping existing learned weights."""
        if delta_neurons > 0:
            for _ in range(delta_neurons):
                if len(self.w1) < 24:
                    self.w1.append([random.gauss(0.0, 0.8) for _ in range(4)])
                    self.b1.append(random.gauss(0.0, 0.2))
                    self.w2.append(random.gauss(0.0, 0.8))
        elif delta_neurons < 0:
            for _ in range(abs(delta_neurons)):
                if len(self.w1) > 1:
                    self.w1.pop()
                    self.b1.pop()
                    self.w2.pop()
        self.params["hidden_neurons"] = float(len(self.w1))
        if delta_synapses != 0:
            cur_f = int(round(self.params.get("synapse_density", 4.0)))
            new_f = max(2, min(4, cur_f + delta_synapses))
            self.params["synapse_density"] = float(new_f)
        h = len(self.w1)
        f_cnt = int(round(self.params.get("synapse_density", 4.0)))
        return {
            "total_nodes": f_cnt + h + 1,
            "hidden_nodes": h,
            "enabled_synapses": h * (f_cnt + 1),
        }

    def rebuild_dataset(self, n_samples: int = 120) -> None:
        dtype = int(round(self.params["dataset_id"]))
        noise = self.params["noise"]
        self.base_samples = []

        for i in range(n_samples):
            label = 1.0 if (i % 2 == 0) else 0.0
            if dtype == 0:  # XOR
                x = random.uniform(0.18, 0.80) * (1 if (i % 4 < 2) else -1)
                y = random.uniform(0.18, 0.80) * (1 if (x > 0) == (label > 0.5) else -1)
            elif dtype == 1:  # Concentric Rings
                r = random.uniform(0.10, 0.34) if label > 0.5 else random.uniform(0.56, 0.84)
                ang = (i / n_samples) * 2.0 * math.pi + random.uniform(-0.08, 0.08)
                x, y = r * math.cos(ang), r * math.sin(ang)
            elif dtype == 2:  # Two Moons
                ang = (i / n_samples) * math.pi
                if label > 0.5:
                    x = math.cos(ang) * 0.62 - 0.22
                    y = math.sin(ang) * 0.62 - 0.14
                else:
                    x = 1.0 - math.cos(ang) * 0.62 - 0.28
                    y = -math.sin(ang) * 0.62 + 0.14
            else:  # Spiral
                t = (i / n_samples) * 2.1 * math.pi
                r = 0.14 + 0.72 * (i / n_samples)
                offset = 0.0 if label > 0.5 else math.pi
                x = r * math.cos(t + offset)
                y = r * math.sin(t + offset)

            x += random.gauss(0.0, noise)
            y += random.gauss(0.0, noise)
            x = max(-0.95, min(0.95, x))
            y = max(-0.95, min(0.95, y))
            self.base_samples.append((x, y, label))

        self._apply_live_swirl()

    def add_interactive_dots(self, norm_x: float, norm_y: float, label: float = 1.0, count: int = 6) -> None:
        """Drop a cluster of custom blue (1.0) or red (0.0) dots at the clicked normalized coordinate [-1, 1]."""
        ang = -self.swirl_phase * 0.45
        ca, sa = math.cos(ang), math.sin(ang)
        bx0 = norm_x * ca - norm_y * sa
        by0 = norm_x * sa + norm_y * ca
        for _ in range(count):
            px = max(-0.94, min(0.94, bx0 + random.gauss(0.0, 0.045)))
            py = max(-0.94, min(0.94, by0 + random.gauss(0.0, 0.045)))
            if len(self.base_samples) >= 140:
                self.base_samples.pop(0)
            self.base_samples.append((px, py, label))
        self._apply_live_swirl()
        self.step_physics()

    def _apply_live_swirl(self) -> None:
        """Applies gentle live orbital rotation and wave breathing so the decision boundary actively tracks moving points."""
        if not self.base_samples:
            return
        dtype = int(round(self.params["dataset_id"]))
        ang = self.swirl_phase * 0.45
        ca, sa = math.cos(ang), math.sin(ang)
        new_samples: List[Tuple[float, float, float]] = []

        for idx, (bx, by, label) in enumerate(self.base_samples):
            if dtype == 1:
                # Concentric rings: wave-star radial modulation + rotation
                theta = math.atan2(by, bx) + ang
                r0 = math.hypot(bx, by)
                scale = 1.0 + 0.16 * math.sin(self.swirl_phase * 1.8 + theta * 3.0)
                rx = r0 * scale * math.cos(theta)
                ry = r0 * scale * math.sin(theta)
            else:
                # Rotate & gently pulse Two Moons, XOR, or Spiral
                pulse = 1.0 + 0.08 * math.sin(self.swirl_phase * 1.5 + idx * 0.1)
                rx = (bx * ca - by * sa) * pulse
                ry = (bx * sa + by * ca) * pulse

            rx = max(-0.96, min(0.96, rx))
            ry = max(-0.96, min(0.96, ry))
            new_samples.append((rx, ry, label))

        self.samples = new_samples

    def rebuild_network(self) -> None:
        h = max(2, int(round(self.params["hidden_neurons"])))
        self.w1 = [[random.gauss(0.0, 0.55) for _ in range(4)] for _ in range(h)]
        self.b1 = [random.gauss(0.0, 0.15) for _ in range(h)]
        self.w2 = [random.gauss(0.0, 0.55) for _ in range(h)]
        self.b2 = 0.0
        self.epoch = 0
        self.history_best = []
        self.history_avg = []

    def reset_generation(self) -> None:
        """Compatibility helper so Reset/Preset buttons re-seed both dataset and weights."""
        self.rebuild_dataset()
        self.rebuild_network()

    def update_param(self, key: str, value: float) -> None:
        old = self.params.get(key)
        self.params[key] = float(value)
        if key in ("dataset_id", "noise") and old != float(value):
            self.rebuild_dataset()
            if key == "dataset_id":
                self.rebuild_network()
        elif key == "hidden_neurons":
            target_h = max(1, min(24, int(round(value))))
            diff = target_h - len(self.w1)
            if diff != 0:
                self.modify_brain_structure(delta_neurons=diff, delta_synapses=0)

    def predict_prob(self, x: float, y: float) -> Tuple[float, List[float]]:
        f_cnt = int(round(self.params.get("synapse_density", 4.0)))
        gain = self.params.get("activation_gain", 1.0)
        feats = [
            x,
            y,
            (x * x + y * y) if f_cnt >= 3 else 0.0,
            (x * y) if f_cnt >= 4 else 0.0,
        ]
        h_acts: List[float] = []
        z_out = self.b2
        for j in range(len(self.w1)):
            s = self.b1[j] + (
                self.w1[j][0] * feats[0]
                + self.w1[j][1] * feats[1]
                + self.w1[j][2] * feats[2]
                + self.w1[j][3] * feats[3]
            )
            hj = math.tanh(max(-15.0, min(15.0, s * gain)))
            h_acts.append(hj)
            z_out += self.w2[j] * hj
        z_out = max(-20.0, min(20.0, z_out))
        prob = 1.0 / (1.0 + math.exp(-z_out))
        return prob, h_acts

    def _train_one_epoch(self) -> None:
        h = len(self.w1)
        n = max(1, len(self.samples))
        lr = self.params["learning_rate"]
        l2 = self.params["l2_reg"]

        dw1 = [[0.0] * 4 for _ in range(h)]
        db1 = [0.0] * h
        dw2 = [0.0] * h
        db2 = 0.0

        total_loss = 0.0
        correct = 0

        for x, y, target in self.samples:
            feats = [x, y, x * x + y * y, x * y]
            prob, h_acts = self.predict_prob(x, y)

            eps = 1e-7
            total_loss += -(target * math.log(prob + eps) + (1.0 - target) * math.log(1.0 - prob + eps))
            if (prob >= 0.5) == (target >= 0.5):
                correct += 1

            # Backpropagation gradients
            dz2 = (prob - target) / n
            db2 += dz2
            for j in range(h):
                dw2[j] += dz2 * h_acts[j]
                dh = dz2 * self.w2[j] * (1.0 - h_acts[j] * h_acts[j])
                db1[j] += dh
                for k in range(4):
                    dw1[j][k] += dh * feats[k]

        # Apply gradient update + L2 decay
        self.b2 -= lr * db2
        for j in range(h):
            self.w2[j] -= lr * (dw2[j] + l2 * self.w2[j])
            self.b1[j] -= lr * db1[j]
            for k in range(4):
                self.w1[j][k] -= lr * (dw1[j][k] + l2 * self.w1[j][k])

        self.epoch += 1
        self.loss = total_loss / n
        self.accuracy = (100.0 * correct) / n

    def step_physics(self) -> bool:
        self.swirl_phase += 0.032
        self._apply_live_swirl()
        steps = max(1, int(round(self.params["steps_per_frame"])))
        for _ in range(steps):
            self._train_one_epoch()
        if self.epoch % 10 == 0:
            self.history_best.append(round(self.accuracy, 1))
            self.history_avg.append(round(max(0.0, (1.0 - self.loss) * 100.0), 1))
            return True
        return False

    def fast_forward_generations(self, num_gens: int = 50) -> Dict[str, Any]:
        for _ in range(num_gens * 5):
            self._train_one_epoch()
        self.history_best.append(round(self.accuracy, 1))
        self.history_avg.append(round(max(0.0, (1.0 - self.loss) * 100.0), 1))
        return self.get_telemetry()

    def get_telemetry(self) -> Dict[str, Any]:
        dname = self.DATASET_NAMES.get(int(round(self.params["dataset_id"])), "Custom")
        return {
            "lab": f"Neural Backprop ({dname})",
            "generation": self.epoch,
            "species": len(self.w1),
            "best_fitness": round(self.accuracy, 1),
            "avg_fitness": round(self.loss, 4),
            "best_ever": round(max(self.history_best) if self.history_best else self.accuracy, 1),
            "params": dict(self.params)
        }
