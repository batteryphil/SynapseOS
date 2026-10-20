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

    def test_learning_pack_update_and_trophy_preservation(self):
        import tempfile
        from workbench.pack_manager import LearningPackManager

        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = LearningPackManager(base_dir=tmpdir)
            self.assertEqual(mgr.profile["active_pack_id"], "pack_1_core")
            self.assertEqual(len(mgr.get_kid_levels()), 7)

            # Award a student badge & verify points increase
            was_new = mgr.award_badge("pack_1_core_L1", points=100, stars=3)
            self.assertTrue(was_new)
            pts_before = mgr.profile["lifetime_points"]

            # Place a dummy old file inside active_pack/ to verify old pack files are purged
            dummy_old = os.path.join(mgr.pack_dir, "old_pack_cache.bin")
            with open(dummy_old, "wb") as f:
                f.write(b"X" * 4096)
            self.assertTrue(os.path.exists(dummy_old))

            # Upgrade to Pack 2 (Cyber Commander Mastery, Levels 8-14)
            res2 = mgr.upgrade_to_next_pack()
            self.assertEqual(res2["new_pack_id"], "pack_2_mastery")
            self.assertFalse(os.path.exists(dummy_old))  # Old pack file deleted to save space!
            self.assertGreater(res2["freed_bytes"], 4096)
            self.assertIn("pack_1_core_L1", res2["earned_badges"])
            self.assertIn("trophy_pack_1_core_complete", res2["earned_badges"])
            self.assertGreater(res2["lifetime_points"], pts_before)
            self.assertEqual(mgr.get_kid_levels()[0]["level"], 8)

            # Reload from disk to verify persistence across restarts
            mgr_reloaded = LearningPackManager(base_dir=tmpdir)
            self.assertEqual(mgr_reloaded.profile["active_pack_id"], "pack_2_mastery")
            self.assertIn("pack_1_core_L1", mgr_reloaded.profile["earned_badges"])
            self.assertEqual(mgr_reloaded.profile["lifetime_points"], res2["lifetime_points"])

    def test_gamified_features_shop_avatars_missions_and_analytics(self):
        import tempfile
        from workbench.pack_manager import (
            LearningPackManager,
            PLAYER_AVATARS,
            TROPHY_SHOP_ITEMS,
            WORLD_MAP_ZONES,
            ALL_TROPHY_PEDESTALS,
        )

        self.assertEqual(len(PLAYER_AVATARS), 6)
        self.assertEqual(len(TROPHY_SHOP_ITEMS), 4)
        self.assertEqual(len(WORLD_MAP_ZONES), 7)
        self.assertEqual(len(ALL_TROPHY_PEDESTALS), 12)

        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = LearningPackManager(base_dir=tmpdir)
            initial_coins = mgr.profile["coins"]
            self.assertGreaterEqual(initial_coins, 200)

            # 1. Cycle avatar
            av = mgr.cycle_avatar()
            self.assertEqual(av["id"], "cyber_bot")
            self.assertEqual(mgr.profile["avatar_idx"], 1)

            # 2. Buy a decoration in the Coin Shop
            res_buy = mgr.buy_or_toggle_shop_item("gold_hull", lang="en")
            self.assertTrue(res_buy["ok"])
            self.assertIn("gold_hull", mgr.profile["unlocked_decorations"])
            self.assertEqual(mgr.profile["coins"], initial_coins - 100)

            # 3. Record Daily Missions progress
            mgr.record_daily_progress("dm_ask_lumi")
            self.assertGreater(mgr.profile["coins"], initial_coins - 100)

            # 4. Record Lab Activity & Sandbox Analytics
            mgr.record_lab_activity("moon_lander", add_seconds=12.0, add_run=True)
            self.assertGreaterEqual(mgr.profile["lab_time_seconds"]["moon_lander"], 12)
            mgr.record_sandbox_run(passed=False, error_snippet="SyntaxError: invalid syntax")
            self.assertIn("Python Syntax / Indentation", mgr.profile["sandbox_stats"]["struggled_concepts"])


if __name__ == "__main__":
    unittest.main()


