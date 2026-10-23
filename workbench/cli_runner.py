#!/usr/bin/env python3
"""
Synapse Studio Launcher & Headless Benchmark Runner
Launches the native GTK3 + Cairo Point-and-Click GUI by default, or runs
high-speed headless evolution/training benchmarks across all 6 AI labs.
"""

import os
import sys
import time
import argparse
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from workbench.labs.moon_lander import NEATMoonLanderLab
from workbench.labs.raycast_car import NEATRaycastCarLab
from workbench.labs.rl_gridworld import RLGridWorldLab
from workbench.labs.cartpole_rl import CartPoleLab
from workbench.labs.nn_playground import NeuralPlaygroundLab
from workbench.labs.swarm_ecosystem import SwarmEcosystemLab
from workbench.labs.prime_attention_lab import PrimeAttentionLab
from workbench.code_generator import generate_lab_python_code
from workbench.curriculum import (
    SCHOOL_CURRICULUM,
    ALL_CURRICULUM_LESSONS,
    get_lesson_by_id,
    verify_lesson_goal,
)
from workbench.pack_manager import LearningPackManager
from workbench.sandbox_runner import run_student_code

LAB_CLASSES = {
    "moon_lander": NEATMoonLanderLab,
    "raycast_car": NEATRaycastCarLab,
    "rl_gridworld": RLGridWorldLab,
    "cartpole_rl": CartPoleLab,
    "nn_playground": NeuralPlaygroundLab,
    "swarm_ecosystem": SwarmEcosystemLab,
    "prime_attention": PrimeAttentionLab,
}


def run_benchmark_all(gens: int = 10) -> Dict[str, Any]:
    """Run all 6 AI labs headlessly and report potato CPU speed & convergence."""
    print(f"\n\033[1;96m⚡ Synapse Studio All-Spectrum AI Benchmark ({gens} Generations/Epochs per Lab)\033[0m")
    print("-" * 78)
    results: Dict[str, Any] = {}

    for lid, cls in LAB_CLASSES.items():
        t0 = time.perf_counter()
        lab = cls()
        stats = lab.fast_forward_generations(gens)
        dt_ms = round((time.perf_counter() - t0) * 1000, 1)
        results[lid] = {"stats": stats, "elapsed_ms": dt_ms}
        print(
            f"  \033[1;92m✓\033[0m {stats['lab']:<42} | "
            f"Best: \033[1;93m{str(stats['best_ever']):>7}\033[0m | "
            f"Time: \033[96m{dt_ms:>6.1f} ms\033[0m"
        )

    print("-" * 78)
    return results


def list_curriculum_lessons() -> None:
    """Print active K-12 school year subject lessons + interactive AI lab curriculum."""
    mgr = LearningPackManager()
    cur_yr = mgr.get_current_school_year()
    yr_pack = mgr.get_active_year_pack()
    subj_lessons = mgr.get_active_subject_lessons()

    print(
        f"\n\033[1;96m🏫 Active K-12 School Year {cur_yr} Curriculum: {yr_pack['title_en']} ({len(subj_lessons)} Core Subjects)\033[0m"
    )
    print("=" * 96)
    for les in subj_lessons:
        print(
            f"  \033[1;93m{les['id']:<14}\033[0m | {les['badge']:<22} | "
            f"\033[1;97m{les['title']}\033[0m ({les['grade_level']})"
        )
        print(f"                 └─ Subject: \033[92m{les['track']}\033[0m [Connected AI Lab: {les['lab_id']}]")

    print(f"\n\033[1;96m🎓 SynapseOS Core AI Lab Tracks ({len(SCHOOL_CURRICULUM)} Missions)\033[0m")
    print("=" * 96)
    for lesson in SCHOOL_CURRICULUM:
        print(
            f"  \033[1;93m{lesson['id']:<14}\033[0m | {lesson['badge']:<22} | "
            f"\033[1;97m{lesson['title']}\033[0m ({lesson['grade_level']})"
        )
        print(f"                 └─ Track: \033[92m{lesson['track']}\033[0m [Lab: {lesson['lab_id']}]")
    print("=" * 96)
    print("Run any subject or AI lesson: \033[96m./synapse curriculum <lesson_id>\033[0m (e.g. y01_math, y08_science, lesson_1_1)")
    print("Switch K-12 School Year (1..12): \033[96m./synapse pack set-year <1..12>\033[0m or \033[96m./synapse pack advance-year\033[0m\n")


def run_curriculum_lesson(lesson_id: str) -> int:
    """Load a school lesson, test its preset simulation, and run its hands-on coding challenge."""
    valid_ids = {l["id"] for l in ALL_CURRICULUM_LESSONS}
    if lesson_id not in valid_ids:
        print(f"\033[91m[!] Unknown lesson ID: {lesson_id}\033[0m")
        list_curriculum_lessons()
        return 1

    lesson = get_lesson_by_id(lesson_id)
    print(f"\n\033[1;96m🎓 {lesson['title']}\033[0m  [{lesson['grade_level']}]")
    print(f"\033[93mBadge:\033[0m   {lesson['badge']}")
    print(f"\033[92mTrack:\033[0m   {lesson['track']}")
    print("-" * 82)
    print(lesson["story"])
    print("\n\033[1;97m📋 Follow-Along Steps:\033[0m")
    for s in lesson["steps"]:
        print(f"  {s}")
    print("-" * 82)

    # 1. Run Lab with Lesson Preset Params
    lab = LAB_CLASSES[lesson["lab_id"]]()
    for k, v in lesson["preset_params"].items():
        lab.update_param(k, v)
    if hasattr(lab, "reset_generation"):
        lab.reset_generation()
    elif hasattr(lab, "reset_q_table"):
        lab.reset_q_table()
    elif hasattr(lab, "reset_ecosystem"):
        lab.reset_ecosystem()
    elif hasattr(lab, "rebuild_simulation"):
        lab.rebuild_simulation()
    elif hasattr(lab, "reset_weights"):
        lab.reset_weights()
        lab.rebuild_dataset()
    lab.fast_forward_generations(25)
    passed, msg = verify_lesson_goal(lesson, lab.get_telemetry())
    status_str = "\033[1;92mUNLOCKED\033[0m" if passed else "\033[1;93mIN PROGRESS\033[0m"
    print(f"\033[1;96m[1/2] Lab Simulation Verification:\033[0m [{status_str}]\n{msg}")

    # 2. Run Hands-On Python Coding Challenge in Sandbox
    print(f"\n\033[1;96m[2/2] Running Hands-On Subject & AI Coding Sandbox...\033[0m")
    res = run_student_code(lesson["coding_challenge"])
    if res["ok"]:
        print(f"\033[1;92m{res['output']}\033[0m")
        if lesson_id.startswith("y"):
            mgr = LearningPackManager()
            mgr.record_subject_grade(lesson_id, score=100)
            mgr.award_badge(lesson_id, points=150, stars=3, coins=50)
        return 0
    else:
        print(f"\033[1;91m{res['output']}\033[0m")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Synapse Studio Point-and-Click AI Workbench & School Suite")
    parser.add_argument("--headless", action="store_true", help="Run in headless CLI mode without opening GUI window")
    parser.add_argument("--benchmark", action="store_true", help="Benchmark all 6 built-in AI labs on CPU")
    parser.add_argument("--list-lessons", action="store_true", help="List all 10 interactive school AI curriculum lessons")
    parser.add_argument("--run-lesson", type=str, help="Run a school lesson simulation + hands-on Python challenge by ID")
    parser.add_argument("--lab", type=str, default="moon_lander", choices=list(LAB_CLASSES.keys()), help="Select AI lab")
    parser.add_argument("--gens", type=int, default=15, help="Generations or epochs to run in headless mode")
    parser.add_argument("--export", type=str, choices=list(LAB_CLASSES.keys()), help="Export standalone Python script for a lab")
    args = parser.parse_args()

    if args.list_lessons:
        list_curriculum_lessons()
        return

    if args.run_lesson:
        sys.exit(run_curriculum_lesson(args.run_lesson))

    if args.benchmark:
        run_benchmark_all(gens=args.gens)
        return

    if args.export:
        lab = LAB_CLASSES[args.export]()
        code = generate_lab_python_code(args.export, lab.params, lab.get_telemetry())
        print(code)
        return

    if args.headless:
        lab = LAB_CLASSES[args.lab]()
        t0 = time.perf_counter()
        stats = lab.fast_forward_generations(args.gens)
        dt_ms = round((time.perf_counter() - t0) * 1000, 1)
        print(f"[✓] {stats['lab']} evolved {args.gens} gens in {dt_ms} ms -> Best: {stats['best_ever']} (Gen {stats['generation']})")
        return

    # Launch native GTK3 + Cairo Point-and-Click GUI
    from workbench.studio_gui import main as gui_main
    gui_main()


if __name__ == "__main__":
    main()

