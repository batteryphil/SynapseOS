"""
Unit & Integration Tests for SynapseOS Phase 2:
  - Pure-Python NEAT Engine (`neat_core.py`)
  - All 6 Interactive Point-and-Click AI Labs (`moon_lander`, `raycast_car`, `rl_gridworld`, `cartpole_rl`, `nn_playground`, `swarm_ecosystem`)
  - Live Python Code Generator (`code_generator.py`)
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from workbench.labs.neat_core import NEATPopulation
from workbench.labs.moon_lander import NEATMoonLanderLab
from workbench.labs.raycast_car import NEATRaycastCarLab
from workbench.labs.rl_gridworld import RLGridWorldLab
from workbench.labs.cartpole_rl import CartPoleLab
from workbench.labs.nn_playground import NeuralPlaygroundLab
from workbench.labs.swarm_ecosystem import SwarmEcosystemLab
from workbench.code_generator import generate_lab_python_code


class TestSynapseWorkbenchLabs(unittest.TestCase):
    def test_neat_core_evolution(self):
        pop = NEATPopulation(num_inputs=4, num_outputs=2, pop_size=20)
        for g in pop.genomes:
            out = g.forward([0.5, -0.2, 0.1, 1.0])
            self.assertEqual(len(out), 2)
            g.fitness = sum(out)
        stats = pop.evolve_generation()
        self.assertEqual(stats["generation"], 1)
        self.assertGreaterEqual(stats["species_count"], 1)

    def test_lab1_moon_lander(self):
        lab = NEATMoonLanderLab()
        lab.update_param("pop_size", 20)
        lab.reset_generation()
        stats = lab.fast_forward_generations(3)
        self.assertGreaterEqual(stats["generation"], 4)
        code = generate_lab_python_code("moon_lander", lab.params, stats)
        self.assertIn("NEATMoonLanderLab", code)

    def test_lab2_raycast_car(self):
        lab = NEATRaycastCarLab()
        lab.update_param("pop_size", 15)
        lab.reset_generation()
        stats = lab.fast_forward_generations(2)
        self.assertGreaterEqual(stats["generation"], 3)
        code = generate_lab_python_code("raycast_car", lab.params, stats)
        self.assertIn("NEATRaycastCarLab", code)

    def test_lab3_rl_gridworld(self):
        lab = RLGridWorldLab()
        stats = lab.fast_forward_generations(15)
        self.assertGreaterEqual(stats["generation"], 15)
        code = generate_lab_python_code("rl_gridworld", lab.params, stats)
        self.assertIn("RLGridWorldLab", code)

    def test_lab4_cartpole_rl(self):
        lab = CartPoleLab()
        lab.update_param("pop_size", 15)
        lab.reset_generation()
        stats = lab.fast_forward_generations(2)
        self.assertGreaterEqual(stats["generation"], 3)
        code = generate_lab_python_code("cartpole_rl", lab.params, stats)
        self.assertIn("CartPoleLab", code)

    def test_lab5_nn_playground(self):
        lab = NeuralPlaygroundLab()
        stats = lab.fast_forward_generations(10)
        self.assertGreater(stats["best_fitness"], 50.0)
        code = generate_lab_python_code("nn_playground", lab.params, stats)
        self.assertIn("NeuralPlaygroundLab", code)

    def test_lab6_swarm_ecosystem(self):
        lab = SwarmEcosystemLab()
        lab.update_param("num_prey", 15)
        lab.reset_ecosystem()
        stats = lab.fast_forward_generations(2)
        self.assertGreaterEqual(stats["generation"], 3)
        code = generate_lab_python_code("swarm_ecosystem", lab.params, stats)
        self.assertIn("SwarmEcosystemLab", code)

    def test_lab7_prime_sliding_window_attention(self):
        from workbench.labs.prime_attention_lab import PrimeAttentionLab
        lab = PrimeAttentionLab()
        lab.update_param("window_size", 64.0)
        stats = lab.fast_forward_generations(3)
        self.assertGreater(stats["best_fitness"], stats["avg_fitness"])
        self.assertGreater(stats["c_tokens_per_sec"], 1000.0)
        code = generate_lab_python_code("prime_attention", lab.params, stats)
        self.assertIn("PrimeAttentionLab", code)

    def test_prime_c_engine_and_compressor(self):
        from cortex.prime_window import CortexSlidingWindowCompressor, benchmark_c_prime_engine
        bench = benchmark_c_prime_engine(num_heads=8, head_dim=64, steps=200)
        self.assertEqual(round(bench["state_kb"], 2), 262.03)
        self.assertGreater(bench["tokens_per_sec"], 1000.0)

        comp = CortexSlidingWindowCompressor(window_tokens=20, head_dim=32)
        chunks = [
            "Irrelevant distractor paragraph about cooking pasta with tomatoes and basil.",
            "Second-order Taylor moment recurrence S2 retains associative passkeys in 262 KB L2 cache.",
            "Another distractor sentence about weather forecasts in Antarctica.",
            "Recent sliding window turn asking about PRIME Moment Attention memory scaling.",
        ]
        res = comp.compress_context("How does PRIME Moment Attention save memory in L2 cache?", chunks, max_evicted_keep=1)
        self.assertLess(res["compressed_tokens_est"], res["original_tokens_est"])
        self.assertIn("262 KB L2 cache", res["compressed_text"])


if __name__ == "__main__":
    unittest.main()

