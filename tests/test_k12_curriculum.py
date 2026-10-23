import json
import os
import tempfile
import unittest

from workbench.curriculum import get_curriculum_for_year, get_lesson_by_id
from workbench.k12_curricula import (
    K12_YEAR_PACKS,
    YEAR_PACK_ORDER,
    get_all_k12_subject_lessons,
)
from workbench.pack_manager import LearningPackManager
from workbench.sandbox_runner import run_student_code


class TestK12RollingCurriculum(unittest.TestCase):
    def test_all_12_years_and_60_traditional_plus_ai_lessons_exist(self):
        """Verify Years 1-12 exist in repo `curricula/` and each has Math, Science, ELA, History, and AI."""
        self.assertEqual(len(YEAR_PACK_ORDER), 12)
        repo_curricula = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "curricula",
        )
        self.assertTrue(os.path.isfile(os.path.join(repo_curricula, "index.json")))

        all_lessons = get_all_k12_subject_lessons()
        self.assertEqual(len(all_lessons), 60)

        expected_subjects = ["math", "science", "ela", "history", "ai_cs"]
        for yr in range(1, 13):
            yid = f"year_{yr:02d}"
            self.assertIn(yid, K12_YEAR_PACKS)
            json_path = os.path.join(repo_curricula, f"{yid}.json")
            self.assertTrue(os.path.isfile(json_path), f"Missing {json_path}")

            with open(json_path, "r", encoding="utf-8") as f:
                disk_pack = json.load(f)

            self.assertEqual(disk_pack["year_number"], yr)
            self.assertEqual(disk_pack["subjects"], expected_subjects)
            self.assertEqual(len(disk_pack["subject_lessons"]), 5)
            self.assertEqual(len(disk_pack["kid_levels"]), 7)

            subj_keys = [les["subject_key"] for les in disk_pack["subject_lessons"]]
            self.assertEqual(subj_keys, expected_subjects)

            # Verify get_curriculum_for_year includes the 5 year subjects at the top
            yr_curr = get_curriculum_for_year(yr)
            self.assertGreaterEqual(len(yr_curr), 19)
            self.assertEqual(yr_curr[0]["id"], f"y{yr:02d}_math")
            self.assertEqual(get_lesson_by_id(f"y{yr:02d}_history")["year_number"], yr)

    def test_one_year_at_a_time_wiper_and_permanent_transcript(self):
        """Verify advancing school years wipes old year files while keeping multi-subject transcript & trophies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = LearningPackManager(base_dir=tmpdir)
            res_y1 = mgr.set_school_year(1)
            self.assertEqual(res_y1["new_pack_id"], "year_01")
            self.assertEqual(mgr.get_current_school_year(), 1)

            # Complete Year 1 Math, Science, ELA, History, AI
            for subj in ("math", "science", "ela", "history", "ai_cs"):
                mgr.record_subject_grade(f"y01_{subj}", score=98)

            # Advance from Year 1 -> Year 2 -> Year 3
            res_y2 = mgr.advance_school_year()
            self.assertEqual(res_y2["new_pack_id"], "year_02")
            self.assertEqual(mgr.get_current_school_year(), 2)
            self.assertGreater(res_y2["freed_bytes"], 1000)

            # Verify only 1 pack file exists in active_pack/ directory
            active_files = os.listdir(mgr.pack_dir)
            self.assertEqual(active_files, ["current_pack.json"])
            with open(mgr.active_pack_file, "r", encoding="utf-8") as f:
                active_data = json.load(f)
            self.assertEqual(active_data["pack_id"], "year_02")

            # Verify Year 1 transcript and Honors badge were permanently preserved!
            transcript = mgr.profile["yearly_transcript"]
            self.assertIn("year_01", transcript)
            self.assertTrue(transcript["year_01"]["graduated"])
            self.assertEqual(transcript["year_01"]["math"], 98)
            self.assertIn("trophy_year_01_honors", mgr.profile["earned_badges"])
            self.assertIn("trophy_year_01_complete", mgr.profile["earned_badges"])

    def test_sample_k12_subject_coding_assignments_execute_cleanly(self):
        """Verify Traditional + AI coding challenges across elementary, middle, and high school run cleanly."""
        sample_ids = [
            "y01_math",
            "y01_ela",
            "y03_science",
            "y05_history",
            "y07_math",
            "y09_math",
            "y11_science",
            "y12_history",
            "y12_ai_cs",
        ]
        for lid in sample_ids:
            les = get_lesson_by_id(lid)
            res = run_student_code(les["coding_challenge"])
            self.assertTrue(res["ok"], f"Lesson {lid} failed: {res['output']}")
