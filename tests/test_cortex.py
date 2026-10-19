"""
Unit & Integration Tests for SynapseOS Phase 1:
  - SQLite FTS5 Sub-Millisecond Knowledge Base (`cortex_kb.sqlite`)
  - Phi-3 Mini Fine-Tuning Dataset & QLoRA Pipeline (`cortex/forge/`)
  - `cortex-phi3:latest` Hybrid RAG & Potato Mode Orchestrator (`cortex/engine.py`)
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cortex.engine import CortexEngine, SystemInspector, CortexKnowledgeDB
from cortex.forge.train_phi3_qlora import validate_pipeline


class TestCortexPhase1(unittest.TestCase):
    def setUp(self):
        self.engine = CortexEngine()
        self.kb = CortexKnowledgeDB()

    def test_system_inspector(self):
        hw = SystemInspector.get_hardware_summary()
        self.assertIn("os", hw)
        self.assertIn("kernel", hw)
        self.assertIn("is_potato", hw)
        self.assertGreater(hw["cpu_cores"], 0)
        self.assertGreater(hw["ram_total_gb"], 0)

    def test_sqlite_fts5_kb_ready_and_fast(self):
        self.assertTrue(self.kb.is_ready(), "SQLite FTS5 KB must exist")
        linux_hits = self.kb.search_linux("boost ram on a potato with zram")
        self.assertGreater(len(linux_hits), 0)
        self.assertIn("zram", linux_hits[0]["command"])
        self.assertLess(linux_hits[0]["retrieval_ms"], 50.0, "FTS5 retrieval must be < 50ms")

    def test_sqlite_fts5_ai_multi_tier(self):
        ai_hits = self.kb.search_ai("neat moon lander rocket")
        self.assertGreater(len(ai_hits), 0)
        top = ai_hits[0]
        self.assertIn("layman_guide", top)
        self.assertIn("math_and_theory", top)
        self.assertIn("hyperparameters", top)
        self.assertIn("code_template", top)
        self.assertIn("debugging_tips", top)

    def test_phi3_qlora_forge_pipeline_validation(self):
        report = validate_pipeline()
        self.assertEqual(report["status"], "READY")
        self.assertGreaterEqual(report["total_samples"], 50)
        self.assertEqual(report["valid_phi3_chatml_samples"], report["total_samples"])
        target_mods = report["qlora_spec"]["lora_config"]["target_modules"]
        self.assertIn("qkv_proj", target_mods)
        self.assertIn("gate_up_proj", target_mods)

    def test_preferred_model_is_cortex_phi3(self):
        if self.engine.is_ollama_available():
            pref = self.engine.get_preferred_model()
            self.assertTrue(pref.startswith("cortex-phi3") or pref == "phi3:mini")

    def test_command_synthesis_and_safety(self):
        res = self.engine.synthesize_command_and_instructions("kill runaway python training process")
        self.assertIn("command", res)
        self.assertIn("pkill", res["command"])
        self.assertEqual(res["safety"], "caution")
        self.assertIn("instructions", res)

    def test_potato_mode_engine(self):
        potato_engine = CortexEngine(potato_mode=True)
        self.assertTrue(potato_engine.potato_mode)
        res = potato_engine.synthesize_command_and_instructions("limit process ram cpu potato")
        self.assertIn("systemd-run", res["command"])


if __name__ == "__main__":
    unittest.main()
