import json
import os
import tempfile
import unittest

from workbench.curriculum import get_curriculum_for_year, get_lesson_by_id
from workbench.k12_curricula import (
    K12_ALL_GRADE_ORDER,
    K12_YEAR_PACKS,
    YEAR_PACK_ORDER,
    get_all_k12_lessons_with_quarters,
    get_all_k12_subject_lessons,
)
from workbench.pack_manager import LearningPackManager
from workbench.sandbox_runner import run_student_code


class TestK12RollingCurriculum(unittest.TestCase):
    def test_all_13_grades_k_to_12_and_325_complete_textbook_lessons_exist(self):
        """Verify Kindergarten (year_00) + Grades 1-12 exist with 6-section textbook lessons and 4 quarters each."""
        self.assertEqual(len(YEAR_PACK_ORDER), 12)
        self.assertEqual(len(K12_ALL_GRADE_ORDER), 13)
        repo_curricula = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "curricula",
        )
        self.assertTrue(os.path.isfile(os.path.join(repo_curricula, "index.json")))

        all_lessons = get_all_k12_subject_lessons()
        self.assertEqual(len(all_lessons), 65)  # 13 grades (K-12) * 5 core subjects

        all_with_quarters = get_all_k12_lessons_with_quarters()
        self.assertEqual(len(all_with_quarters), 325)  # 65 courses + 260 quarterly units

        expected_subjects = ["math", "science", "ela", "history", "ai_cs"]
        for yr in range(0, 13):
            yid = f"year_{yr:02d}"
            self.assertIn(yid, K12_YEAR_PACKS)
            json_path = os.path.join(repo_curricula, f"{yid}.json")
            self.assertTrue(os.path.isfile(json_path), f"Missing {json_path}")

            with open(json_path, "r", encoding="utf-8") as f:
                disk_pack = json.load(f)

            self.assertEqual(disk_pack["year_number"], yr)
            self.assertEqual(disk_pack["subjects"], expected_subjects)
            self.assertEqual(len(disk_pack["subject_lessons"]), 5)
            self.assertEqual(len(disk_pack["quarterly_lessons"]), 20)
            self.assertEqual(len(disk_pack["kid_levels"]), 7)

            subj_keys = [les["subject_key"] for les in disk_pack["subject_lessons"]]
            self.assertEqual(subj_keys, expected_subjects)

            # Verify every subject lesson has all 6 textbook sections + interactive multiple-choice quiz
            for les in disk_pack["subject_lessons"]:
                self.assertIn("standards", les)
                self.assertEqual(len(les["four_quarter_syllabus"]), 4)
                self.assertGreaterEqual(len(les["vocabulary"]), 3)
                self.assertGreaterEqual(len(les["worked_examples"]), 2)
                self.assertGreaterEqual(len(les["practice_quiz"]), 3)
                for q in les["practice_quiz"]:
                    self.assertIn("choices", q)
                    self.assertEqual(len(q["choices"]), 4)
                    self.assertIn(q.get("correct_choice"), ("A", "B", "C", "D"))
                self.assertEqual(les["rubric"]["total_points"], 100)
                self.assertIn("SECTION 1 — CORE TEXTBOOK LESSON", les["story_challenge"])
                self.assertIn("SECTION 5 — TRADITIONAL PRACTICE WORKSHEET", les["story_challenge"])

            # Verify get_curriculum_for_year includes the 5 year subjects + 20 quarters at the top
            yr_curr = get_curriculum_for_year(yr)
            self.assertGreaterEqual(len(yr_curr), 39)
            self.assertEqual(yr_curr[0]["id"], f"y{yr:02d}_math")
            self.assertEqual(get_lesson_by_id(f"y{yr:02d}_history")["year_number"], yr)
            self.assertEqual(get_lesson_by_id(f"y{yr:02d}_science_q2")["quarter"], 2)

    def test_one_year_at_a_time_wiper_and_permanent_transcript(self):
        """Verify advancing school years (including Kindergarten -> Grade 1) wipes old year files while keeping transcript."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = LearningPackManager(base_dir=tmpdir)
            res_yk = mgr.set_school_year("K")
            self.assertEqual(res_yk["new_pack_id"], "year_00")
            self.assertEqual(mgr.get_current_school_year(), 0)

            res_y1 = mgr.advance_school_year()
            self.assertEqual(res_y1["new_pack_id"], "year_01")
            self.assertEqual(mgr.get_current_school_year(), 1)

            # Complete Year 1 Math, Science, ELA, History, AI
            for subj in ("math", "science", "ela", "history", "ai_cs"):
                mgr.record_subject_grade(f"y01_{subj}", score=98)

            # Advance from Year 1 -> Year 2
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

    def test_multi_student_classroom_roster_and_printable_report_card_export(self):
        """Verify multi-student profile switching and printable HTML/TXT report card export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = LearningPackManager(base_dir=tmpdir)
            mgr.set_school_year(3)
            mgr.record_subject_grade("y03_math", score=100)

            # Switch to Cadet Leo (starts cleanly at Year 4)
            res_leo = mgr.switch_student("Cadet Leo")
            self.assertTrue(res_leo["ok"])
            self.assertEqual(mgr.profile["player_name"], "Cadet Leo")
            self.assertEqual(mgr.get_current_school_year(), 4)
            mgr.set_school_year("K")
            self.assertEqual(mgr.get_current_school_year(), 0)

            # Switch back to Cadet Nova (retains Year 3 & 100% Math score!)
            res_nova = mgr.switch_student("Cadet Nova")
            self.assertTrue(res_nova["ok"])
            self.assertEqual(mgr.profile["player_name"], "Cadet Nova")
            self.assertEqual(mgr.get_current_school_year(), 3)
            self.assertEqual(mgr.profile["yearly_transcript"]["year_03"]["math"], 100)

            # Export printable HTML & TXT report card
            exp = mgr.export_printable_report_card(output_dir=tmpdir)
            self.assertTrue(exp["ok"])
            self.assertTrue(os.path.isfile(exp["html_path"]))
            self.assertTrue(os.path.isfile(exp["txt_path"]))
            with open(exp["html_path"], "r", encoding="utf-8") as f:
                html_doc = f.read()
            self.assertIn("Cadet Nova", html_doc)
            self.assertIn("Grade 3", html_doc)

    def test_all_65_k12_subject_coding_assignments_and_91_kid_levels_execute_cleanly(self):
        """Verify all 65 K-12 subject coding worksheets (K-12) and all 91 Kid Mode levels run cleanly."""
        for les in get_all_k12_subject_lessons(include_kindergarten=True):
            lid = les["id"]
            res = run_student_code(les["coding_challenge"])
            self.assertTrue(res["ok"], f"Lesson {lid} failed: {res['output']}")
            self.assertIn("100/100", res["output"], f"Lesson {lid} missing 100/100 score")

        for yid in K12_ALL_GRADE_ORDER:
            klevels = K12_YEAR_PACKS[yid]["kid_levels"]
            self.assertEqual(len(klevels), 7)
            for kl in klevels:
                for key in ("level", "lab_id", "title_en", "title_fr", "speech_en", "speech_fr", "preset"):
                    self.assertIn(key, kl, f"Missing {key} in {yid}")


if __name__ == "__main__":
    unittest.main()
