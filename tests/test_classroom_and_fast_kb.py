import os
import tempfile
import time
import unittest
from unittest.mock import patch

from cortex.engine import CortexEngine
from workbench.classroom_hub import ClassroomHubManager
from workbench.safe_media_sandbox import SafeMediaSandboxWidget


class TestFastSubMillisecondAndClassroomHub(unittest.TestCase):
    def setUp(self):
        self.engine = CortexEngine()

    def test_instant_1ms_button_never_blocks_on_ollama(self):
        """
        Regression test for 2009 MacBook Pro reviewer bug:
        Clicking '⚡ Instant (<1ms)' (force_llm=False) must NEVER invoke query_local_ollama()
        even for lab IDs like 'raycast_car', 'swarm_ecosystem', or arbitrary user text.
        """
        queries = [
            "moon_lander",
            "raycast_car",
            "rl_gridworld",
            "cartpole_rl",
            "nn_playground",
            "swarm_ecosystem",
            "prime_attention",
            "unmatched_custom_student_question_xyz",
        ]
        with patch.object(self.engine, "query_local_ollama", side_effect=AssertionError("Should NOT call Ollama when force_llm=False!")):
            for q in queries:
                t0 = time.perf_counter()
                res = self.engine.explain_ai_concept(q, force_llm=False)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                self.assertIn("title", res)
                self.assertIn("SQLite FTS5", res.get("source", ""))
                self.assertLess(elapsed_ms, 25.0, f"Query '{q}' took {elapsed_ms:.2f}ms!")

            for cmd_q in ["check free memory", "unmatched_weird_linux_command_xyz"]:
                t0 = time.perf_counter()
                cmd_res = self.engine.synthesize_command_and_instructions(cmd_q, force_llm=False)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                self.assertIn("command", cmd_res)
                self.assertLess(elapsed_ms, 25.0)

    def test_classroom_hub_broadcast_schedule_files_and_hands_up(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "hub_state.json")
            files_dir = os.path.join(tmpdir, "shared_files")
            hub = ClassroomHubManager(state_path=state_file, shared_files_dir=files_dir, enable_udp=False)

            # 1. Schedule management
            initial_sched = hub.get_schedule()
            self.assertGreaterEqual(len(initial_sched), 4)
            updated_sched = hub.add_schedule_item(
                period="Period 5 (13:00 - 13:45)",
                title="Robotics Challenge",
                lab_id="raycast_car",
                mode="Student Mode",
            )
            self.assertEqual(len(updated_sched), len(initial_sched) + 1)

            # 2. File attachment & Course upload
            sample_py = os.path.join(tmpdir, "custom_reward.py")
            with open(sample_py, "w", encoding="utf-8") as f:
                f.write("def custom_reward(x): return x * 2.0\n")
            attached_name = hub.attach_file(sample_py)
            self.assertEqual(attached_name, "custom_reward.py")
            self.assertIn("custom_reward", hub.read_attached_file("custom_reward.py"))

            course = hub.upload_course(
                title="Teacher Custom Lidar Course",
                lab_id="raycast_car",
                description="Use 5 lasers to steer smoothly.",
                starter_code="print('Hello Classroom')",
                attached_files=[attached_name],
            )
            self.assertEqual(course["title"], "Teacher Custom Lidar Course")

            # 3. 1-Click LAN Broadcast
            bcast = hub.broadcast_to_classroom(
                title="All Students: Start Raycast Car!",
                message="Load custom_reward.py and test 5 laps.",
                lab_id="raycast_car",
                code_snippet="print('LAN Broadcast')",
                attached_files=[attached_name],
            )
            self.assertEqual(hub.get_state()["active_broadcast"]["id"], bcast["id"])

            # 4. Student Raise Hand & Teacher Reply
            hand = hub.raise_hand(
                student_name="Djiby (2009 MacBook Pro)",
                question="How do I make the car slow down before sharp turns?",
                lab_id="raycast_car",
                level="Level 2",
            )
            self.assertEqual(hand["status"], "open")

            replied = hub.reply_to_hand(
                hand["id"],
                "Lower throttle to 0.4 when center raycast distance < 0.35!",
            )
            self.assertIsNotNone(replied)
            self.assertEqual(replied["status"], "answered")
            self.assertIn("Lower throttle", replied["teacher_reply"])

    def test_safe_media_sandbox_episodes_and_kiwix_search(self):
        episodes = SafeMediaSandboxWidget.get_episodes()
        self.assertGreaterEqual(len(episodes), 4)
        self.assertIn("Moon", episodes[0]["title"])

        kiwix_hits = SafeMediaSandboxWidget.search_encyclopedia("ternary")
        self.assertGreaterEqual(len(kiwix_hits), 1)
        self.assertIn("Ternary", kiwix_hits[0]["title"])


if __name__ == "__main__":
    unittest.main()
