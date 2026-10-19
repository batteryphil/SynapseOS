"""
SynapseOS Classroom Hands-On Coding Sandbox Runner (`workbench/sandbox_runner.py`)
Executes student Python scripts in an isolated subprocess with a strict timeout
guardrail (preventing accidental infinite loops from freezing a classroom PC)
and translates Python errors into kid-friendly hints.
"""

import os
import sys
import time
import subprocess
from typing import Dict, Any

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def explain_python_error_for_kids(stderr_text: str) -> str:
    """Translate standard Python tracebacks into encouraging, kid-friendly hints."""
    if "SyntaxError" in stderr_text:
        return "💡 Kid Tutor Hint: Check for a missing parenthesis `)`, quote `'`, or colon `:` at the end of an `if`/`for`/`def` line!"
    if "IndentationError" in stderr_text:
        return "💡 Kid Tutor Hint: Python uses spaces at the start of a line to group code. Make sure lines inside a loop or function are lined up evenly!"
    if "NameError" in stderr_text:
        return "💡 Kid Tutor Hint: Python saw a variable or function name it doesn't recognize yet. Check the spelling and capitalization!"
    if "ZeroDivisionError" in stderr_text:
        return "💡 Kid Tutor Hint: Your math formula divided a number by `0`! Try adding a tiny number like `+ 0.001` to the bottom."
    if "IndexError" in stderr_text or "KeyError" in stderr_text:
        return "💡 Kid Tutor Hint: You tried to grab an item from a list or dictionary that doesn't exist at that position."
    return "💡 Kid Tutor Hint: Read the last line of the error message above—or click '🤖 Ask Cortex Tutor' to have AI fix it with you!"


def run_student_code(code_str: str, timeout_sec: float = 8.0) -> Dict[str, Any]:
    """Execute student Python code safely with timeout protection."""
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{PROJECT_ROOT}:{existing_pp}" if existing_pp else PROJECT_ROOT

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code_str],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        if proc.returncode == 0:
            out = proc.stdout.strip() or "(Code ran with no printed output. Add a `print(...)` statement!)"
            return {
                "ok": True,
                "elapsed_ms": elapsed_ms,
                "output": f"✅ Success ({elapsed_ms} ms):\n{out}"
            }
        else:
            err = proc.stderr.strip()
            hint = explain_python_error_for_kids(err)
            return {
                "ok": False,
                "elapsed_ms": elapsed_ms,
                "output": f"⚠️ Oops! Python reported an error ({elapsed_ms} ms):\n{err}\n\n{hint}"
            }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "elapsed_ms": round(timeout_sec * 1000, 1),
            "output": (
                f"⏱️ Time Limit Reached ({timeout_sec}s)!\n"
                "💡 Kid Tutor Hint: Your code took longer than 8 seconds (maybe a `while` loop never finished?). "
                "Try lowering the number of generations or steps!"
            )
        }
