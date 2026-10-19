#!/usr/bin/env python3
"""
Unit & Integration Tests for SynapseOS School Curriculum & Hands-On Coding Sandbox
Verifies all 10 interactive classroom lessons, badge verifiers, student code sandbox,
timeout protection, and kid-friendly Python error tutor hints.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from workbench.curriculum import (
    SCHOOL_CURRICULUM,
    LAB_EXAMPLES,
    get_examples_for_lab,
    get_lessons_for_lab,
    get_lesson_by_id,
    verify_lesson_goal,
)
from workbench.sandbox_runner import run_student_code, explain_python_error_for_kids


class TestSchoolCurriculumAndSandbox(unittest.TestCase):
    def test_01_all_14_lessons_7_labs_and_35_examples_covered(self):
        """Ensure all 14 lessons and 35 lab examples (5 per lab) exist across all 7 AI labs."""
        self.assertEqual(len(SCHOOL_CURRICULUM), 14)
        covered_labs = {lesson["lab_id"] for lesson in SCHOOL_CURRICULUM}
        expected_labs = {
            "moon_lander",
            "raycast_car",
            "rl_gridworld",
            "cartpole_rl",
            "nn_playground",
            "swarm_ecosystem",
            "prime_attention",
        }
        self.assertEqual(covered_labs, expected_labs)

        # Verify 5 examples for each of the 7 labs (35 total examples)
        self.assertEqual(set(LAB_EXAMPLES.keys()), expected_labs)
        for lab_id in expected_labs:
            exs = get_examples_for_lab(lab_id)
            self.assertEqual(len(exs), 5, f"Expected 5 examples for {lab_id}")

        for lesson in SCHOOL_CURRICULUM:
            self.assertTrue(lesson["title"])
            self.assertTrue(lesson["badge"])
            self.assertGreaterEqual(len(lesson["steps"]), 3)
            self.assertIn("HANDS-ON CODING CHALLENGE", lesson["coding_challenge"])
            self.assertEqual(get_lesson_by_id(lesson["id"])["id"], lesson["id"])

    def test_02_get_lessons_for_lab(self):
        """Verify lab-specific lesson filtering works."""
        moon_lessons = get_lessons_for_lab("moon_lander")
        self.assertGreaterEqual(len(moon_lessons), 2)
        nn_lessons = get_lessons_for_lab("nn_playground")
        self.assertGreaterEqual(len(nn_lessons), 2)

    def test_03_badge_verification_logic(self):
        """Verify verify_lesson_goal unlocks badges when target metrics are met."""
        lesson1 = get_lesson_by_id("lesson_1_1")
        self.assertIsNotNone(lesson1)

        # Failing telemetry
        passed_low, msg_low = verify_lesson_goal(lesson1, {"generation": 2, "best_ever": 40.0})
        self.assertFalse(passed_low)
        self.assertIn("Keep experimenting", msg_low)

        # Passing telemetry
        passed_high, msg_high = verify_lesson_goal(lesson1, {"generation": 6, "best_ever": 250.0})
        self.assertTrue(passed_high)
        self.assertIn("MISSION ACCOMPLISHED", msg_high)
        self.assertIn(lesson1["badge"], msg_high)

        # NN accuracy goal check (Lesson 5.1)
        lesson5 = get_lesson_by_id("lesson_5_1")
        passed_nn, msg_nn = verify_lesson_goal(lesson5, {"best_ever": 95.5})
        self.assertTrue(passed_nn)
        self.assertIn("Pattern Wizard", msg_nn)

    def test_04_all_10_hands_on_coding_challenges_execute(self):
        """Execute every lesson's hands-on student Python challenge in the sandbox."""
        for lesson in SCHOOL_CURRICULUM:
            res = run_student_code(lesson["coding_challenge"], timeout_sec=6.0)
            self.assertTrue(
                res["ok"],
                f"Lesson {lesson['id']} coding challenge failed: {res['output']}",
            )
            self.assertIn("Success", res["output"])

    def test_05_kid_friendly_error_explanations(self):
        """Verify syntax, name, and math errors return friendly tutor hints."""
        bad_code = "rocket_fuel = 100\nprint(rocket_feul)\n"
        res = run_student_code(bad_code, timeout_sec=3.0)
        self.assertFalse(res["ok"])
        self.assertIn("NameError", res["output"])
        self.assertIn("Kid Tutor Hint:", res["output"])

        zero_div_hint = explain_python_error_for_kids("ZeroDivisionError: division by zero")
        self.assertIn("divided a number by `0`", zero_div_hint)

    def test_06_infinite_loop_protection(self):
        """Ensure student infinite loops are safely stopped by the sandbox timeout."""
        loop_code = "while True:\n    pass\n"
        res = run_student_code(loop_code, timeout_sec=0.4)
        self.assertFalse(res["ok"])
        self.assertIn("Time Limit Reached", res["output"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
