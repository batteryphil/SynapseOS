"""
Lab 7: PRIME Moment Sliding-Window Attention Lab
Interactive real-time simulation of Hybrid Sliding-Window + Second-Order Taylor
Moment Recurrent Attention (https://github.com/batteryphil/PRIME-Moment-Attention).
Zero external Python dependencies (Pure Python + C99 `libprime.so` via ctypes).
"""

import math
import random
from typing import Any, Dict, List
from cortex.prime_window import HybridSlidingWindowPrimeEngine, benchmark_c_prime_engine


class PrimeAttentionLab:
    VARIABLE_SPECS = [
        {"key": "window_size", "label": "Sliding Window Size (W)", "desc": "Exact local Softmax KV window before eviction into PRIME", "min": 16.0, "max": 256.0, "step": 16.0, "default": 64.0},
        {"key": "decay", "label": "Moment Decay (λ)", "desc": "Exponential retention horizon for S0, S1, S2 states", "min": 0.980, "max": 0.9999, "step": 0.0005, "default": 0.9990},
        {"key": "alpha", "label": "Window vs PRIME Blend (α)", "desc": "0.0 = Pure PRIME Moment, 0.5 = Hybrid, 1.0 = Window Only", "min": 0.0, "max": 1.0, "step": 0.05, "default": 0.45},
        {"key": "head_dim", "label": "Head Dimension (D)", "desc": "Per-head dimension (O(D^2) state size in L2 cache)", "min": 16.0, "max": 64.0, "step": 16.0, "default": 32.0},
        {"key": "use_qk_norm", "label": "QK-Norm (1=On, 0=Parabolic Rebound)", "desc": "Prevents Taylor polynomial P(x)=1+x+0.5x^2 rebound for x < -1", "min": 0.0, "max": 1.0, "step": 1.0, "default": 1.0},
        {"key": "distractor_gap", "label": "Passkey Distractor Gap (N)", "desc": "Tokens between planted needle and retrieval query", "min": 32.0, "max": 1024.0, "step": 32.0, "default": 256.0},
    ]

    GAPS = [32, 64, 128, 256, 512, 1024]

    def __init__(self):
        self.params: Dict[str, float] = {s["key"]: s["default"] for s in self.VARIABLE_SPECS}
        self.epoch = 0
        self.history_best: List[float] = []  # Hybrid PRIME Retention % at target gap
        self.history_avg: List[float] = []   # Linear ELU+1 Retention % at target gap

        self.curve_hybrid: List[float] = [0.99, 0.98, 0.94, 0.88, 0.76, 0.62]
        self.curve_window_only: List[float] = [1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
        self.curve_linear_elu: List[float] = [0.55, 0.35, 0.18, 0.08, 0.04, 0.01]

        self.s2_heatmap: List[List[float]] = [[0.0] * 12 for _ in range(12)]
        self.c_bench: Dict[str, Any] = benchmark_c_prime_engine(num_heads=8, head_dim=64, steps=500)
        self.rebuild_simulation()

    def rebuild_simulation(self) -> None:
        D = max(16, int(round(self.params["head_dim"])))
        W = max(8, int(round(self.params["window_size"])))
        lam = float(self.params["decay"])
        alpha = float(self.params["alpha"])
        qk_norm = bool(round(self.params["use_qk_norm"]) >= 1)

        self.engine = HybridSlidingWindowPrimeEngine(
            num_heads=8,
            head_dim=D,
            window_size=W,
            decay=lam,
            alpha=alpha,
            use_qk_norm=qk_norm,
        )
        self._evaluate_retention_curves()

    def update_param(self, key: str, value: float) -> None:
        self.params[key] = float(value)
        self.rebuild_simulation()

    def _evaluate_retention_curves(self) -> None:
        D = max(16, int(round(self.params["head_dim"])))
        W = max(8, int(round(self.params["window_size"])))
        lam = float(self.params["decay"])
        alpha = float(self.params["alpha"])
        qk_norm = bool(round(self.params["use_qk_norm"]) >= 1)

        rng = random.Random(42 + (self.epoch % 7))
        k_needle = [rng.gauss(0.0, 1.0) for _ in range(D)]
        kn_norm = math.sqrt(sum(x * x for x in k_needle)) + 1e-6
        k_needle = [x / kn_norm for x in k_needle]

        v_needle = [rng.gauss(0.0, 1.0) for _ in range(D)]
        vn_norm = math.sqrt(sum(x * x for x in v_needle)) + 1e-6
        v_needle = [x / vn_norm for x in v_needle]

        # Run real 2nd-order PRIME state on a 12-dim slice for 60 FPS interactivity
        D_sim = 12
        kn = k_needle[:D_sim]
        vn = v_needle[:D_sim]
        if not qk_norm:
            kn = [x * 2.5 for x in kn]

        S0 = list(vn)
        S1 = [[kn[d] * vn[e] for e in range(D_sim)] for d in range(D_sim)]
        S2 = [[(kn[d] * kn[d]) * vn[e] for e in range(D_sim)] for d in range(D_sim)]

        hybrid_vals: List[float] = []
        win_vals: List[float] = []
        lin_vals: List[float] = []

        # Step through distractor noise and compute analytical + recurrent retention across GAPS
        for step in range(24):
            kd = [rng.gauss(0.0, 1.0) for _ in range(D_sim)]
            kd_n = math.sqrt(sum(x * x for x in kd)) + 1e-6
            kd = [x / kd_n for x in kd]
            if not qk_norm:
                kd = [x * 2.6 for x in kd]
            vd = [rng.gauss(0.0, 0.25) for _ in range(D_sim)]
            for d in range(D_sim):
                S0[d] = lam * S0[d] + vd[d]
                kd_val = kd[d]
                kd_sq = kd_val * kd_val
                row1 = S1[d]
                row2 = S2[d]
                for e in range(D_sim):
                    ve = vd[e]
                    row1[e] = lam * row1[e] + kd_val * ve
                    row2[e] = lam * row2[e] + kd_sq * ve

        self.s2_heatmap = S2

        for g in self.GAPS:
            # 1. Pure Sliding Window: 1.0 if inside window W, else 0.0 (evicted!)
            win_cos = 1.0 if g <= W else 0.0
            win_vals.append(win_cos)

            # 2. Second-order PRIME Moment retention curve (governed by lambda^g & QK-Norm stability)
            signal = math.pow(lam, g)
            noise_accum = math.sqrt((1.0 - math.pow(lam * lam, g)) / max(1e-5, 1.0 - lam * lam)) / math.sqrt(D * 2.0)
            if not qk_norm:
                # Parabolic rebound P(x)=1+x+0.5x^2 amplifies negative-logit distractor variance by ~6x
                noise_accum *= 5.8
            prime_cos = signal / math.sqrt(signal * signal + noise_accum * noise_accum + 1e-6)
            if g <= W:
                hyb_cos = alpha * 1.0 + (1.0 - alpha) * prime_cos
            else:
                hyb_cos = (1.0 - alpha * 0.18) * prime_cos
            hybrid_vals.append(max(0.0, min(1.0, hyb_cos)))

            # 3. First-order ELU+1 Linear Attention baseline (rapidly saturates denominator)
            lin_noise = math.sqrt(g) / math.sqrt(D * 0.45)
            lin_cos = (signal * 0.75) / math.sqrt(signal * signal + lin_noise * lin_noise + 1e-6)
            lin_vals.append(max(0.0, min(1.0, lin_cos)))

        self.curve_hybrid = hybrid_vals
        self.curve_window_only = win_vals
        self.curve_linear_elu = lin_vals

    def step_physics(self) -> bool:
        self.epoch += 1
        if self.epoch % 6 == 0:
            self._evaluate_retention_curves()
            target_gap = int(round(self.params["distractor_gap"]))
            idx = min(range(len(self.GAPS)), key=lambda i: abs(self.GAPS[i] - target_gap))
            best_pct = round(self.curve_hybrid[idx] * 100.0, 1)
            lin_pct = round(self.curve_linear_elu[idx] * 100.0, 1)
            self.history_best.append(best_pct)
            self.history_avg.append(lin_pct)
            if len(self.history_best) > 80:
                self.history_best.pop(0)
                self.history_avg.pop(0)
            return True
        return False

    def fast_forward_generations(self, num_gens: int = 25) -> Dict[str, Any]:
        for _ in range(num_gens):
            self.epoch += 6
            self._evaluate_retention_curves()
            target_gap = int(round(self.params["distractor_gap"]))
            idx = min(range(len(self.GAPS)), key=lambda i: abs(self.GAPS[i] - target_gap))
            self.history_best.append(round(self.curve_hybrid[idx] * 100.0, 1))
            self.history_avg.append(round(self.curve_linear_elu[idx] * 100.0, 1))
        return self.get_telemetry()

    def get_telemetry(self) -> Dict[str, Any]:
        target_gap = int(round(self.params["distractor_gap"]))
        idx = min(range(len(self.GAPS)), key=lambda i: abs(self.GAPS[i] - target_gap))
        hyb_pct = round(self.curve_hybrid[idx] * 100.0, 1)
        lin_pct = round(self.curve_linear_elu[idx] * 100.0, 1)
        D = max(16, int(round(self.params["head_dim"])))
        state_kb = round(((2 * D * D + 3 * D + 1) * 8 * 4) / 1024.0, 2)
        return {
            "lab": f"PRIME Moment Sliding-Window (W={int(self.params['window_size'])}, {state_kb}KB State)",
            "generation": self.epoch,
            "species": int(self.params["window_size"]),
            "best_fitness": hyb_pct,
            "avg_fitness": lin_pct,
            "best_ever": round(max(self.history_best) if self.history_best else hyb_pct, 1),
            "params": dict(self.params),
            "c_tokens_per_sec": round(self.c_bench.get("tokens_per_sec", 0.0), 1),
            "state_kb": state_kb,
        }
