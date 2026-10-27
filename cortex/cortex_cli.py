#!/usr/bin/env python3
"""
Cortex: The System-Level AI Assistant for SynapseOS
Powered by Hybrid SQLite FTS5 (<1ms) + Fine-Tuned `cortex-phi3` (Phi-3 Mini).
"""

import sys
import os
import argparse
import subprocess
import shutil

# Ensure local package path resolution even when invoked via /usr/local/bin symlink
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from cortex.engine import CortexEngine

# ANSI Color Codes
BOLD = "\033[1m"
RESET = "\033[0m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"


def print_banner():
    banner = f"""{CYAN}{BOLD}
   ____ ___  ____ _____  _____  _____ ___  ____ 
  / __// _ \\/ __//_  _/ / __/ |/ / _ \\/ __// __/
 / /__/ // / /    / /  / _/ /    / // /\\ \\ _\\ \\  
 \\___/\\___/_/    /_/  /___//_/|_/\\___/___//___/  
{RESET}{DIM}  SynapseOS Potato-Grade Linux Guide & AI Experimentation Mentor (cortex-phi3){RESET}
"""
    print(banner)


def handle_sys(engine: CortexEngine):
    hw = engine.system_info
    kb_ok = engine.kb.is_ready()
    pref_model = engine.get_preferred_model() if engine.is_ollama_available() else None

    print(f"\n{BOLD}🖥️  System, Potato Budget & AI Engine Diagnostics:{RESET}")
    print(f"  {CYAN}OS / Kernel:{RESET}      {hw['os']} ({hw['kernel']})")
    print(f"  {CYAN}CPU Threads:{RESET}      {hw['cpu_cores']} logical cores")
    print(f"  {CYAN}System RAM:{RESET}       {hw['ram_avail_gb']} GB free / {hw['ram_total_gb']} GB total")
    print(f"  {CYAN}Hardware Profile:{RESET} {'🥔 Potato Mode Active (<4.5GB RAM / Low-Spec)' if engine.potato_mode else '🚀 Workstation Mode (Potato-Compatible)'}")

    if hw["gpus"]:
        print(f"  {CYAN}Accelerators:{RESET}")
        for gpu in hw["gpus"]:
            print(f"    • {GREEN}{gpu}{RESET}")
    else:
        print(f"  {CYAN}Accelerators:{RESET}     {DIM}CPU Vector Mode (AVX2/OpenBLAS){RESET}")

    kb_str = f"🟢 Online ({engine.kb.db_path})" if kb_ok else "🔴 Missing (run `cortex forge --rebuild`)"
    print(f"  {CYAN}FTS5 Knowledge:{RESET}   {kb_str}")

    if pref_model:
        print(f"  {CYAN}Active SLM:{RESET}       🟢 {BOLD}{pref_model}{RESET} (via local Ollama)")
    else:
        print(f"  {CYAN}Active SLM:{RESET}       ⚪ Offline Mode (Sub-millisecond SQLite FTS5 Active)")
    print()


def handle_cmd(engine: CortexEngine, query: str, auto_exec: bool = False, force_llm: bool = False):
    res = engine.synthesize_command_and_instructions(query, force_llm=force_llm)
    safety_eval = res.get("safety_eval") or engine.evaluate_command_safety(res.get("command", ""), res.get("safety", "safe"))

    safety_val = res.get("safety", "safe").lower()
    safety_color = GREEN if safety_val == "safe" else (YELLOW if safety_val == "caution" else RED)
    safety_label = safety_val.upper()

    print(f"\n{BOLD}🎯 Goal:{RESET} {res.get('summary', query)}")
    if res.get("source"):
        print(f"{DIM}⚡ Engine: {res['source']}{RESET}")

    print(f"\n{BOLD}💡 Recommended Command:{RESET}")
    print(f"   {GREEN}{BOLD}{res['command']}{RESET}")

    if res.get("alternative"):
        print(f"   {DIM}Alternative: {res['alternative']}{RESET}")

    breakdown = res.get("flag_breakdown") or engine.explain_command_breakdown(res.get("command", ""))
    if breakdown:
        print(f"\n{BOLD}🔎 Glass-Box Command & Flag Breakdown:{RESET}")
        for item in breakdown:
            print(f"   • {item}")

    if res.get("explanation"):
        print(f"\n{BOLD}🔍 How It Works:{RESET}")
        print(f"   {res['explanation']}")

    print(f"\n{BOLD}📖 Step-by-Step Instructions:{RESET}")
    for i, step in enumerate(res.get("instructions", []), 1):
        print(f"   {CYAN}{i}.{RESET} {step}")

    print(f"\n{BOLD}🛡️  Safety Rating:{RESET} {safety_color}[{safety_label}]{RESET} ({safety_eval.get('category', 'verified_safe')})")
    if res.get("safety_note"):
        print(f"   {YELLOW}⚠️  {res['safety_note']}{RESET}")

    print()

    if not safety_eval.get("allowed", True):
        print(f"{RED}{BOLD}✗ Blocked by SynapseOS Safety Shield:{RESET} {safety_eval.get('reason')}")
        if safety_eval.get("safe_alternative"):
            print(f"{GREEN}💡 Safe Read-Only / Dry-Run Alternative:{RESET} {BOLD}{safety_eval['safe_alternative']}{RESET}")
        return

    if auto_exec:
        print(f"{DIM}Auto-executing command...{RESET}")
        subprocess.run(res["command"], shell=True)
        return

    if sys.stdin.isatty():
        choice = input(f"{BOLD}Run this command now? [y/N/c(opy)]: {RESET}").strip().lower()
        if choice in ["y", "yes"]:
            print(f"\n{DIM}--- Running: {res['command']} ---{RESET}")
            subprocess.run(res["command"], shell=True)
        elif choice in ["c", "copy"]:
            if shutil.which("xclip"):
                subprocess.run(f"echo -n {repr(res['command'])} | xclip -selection clipboard", shell=True)
                print(f"{GREEN}✓ Copied to clipboard.{RESET}")
            elif shutil.which("wl-copy"):
                subprocess.run(f"echo -n {repr(res['command'])} | wl-copy", shell=True)
                print(f"{GREEN}✓ Copied to clipboard.{RESET}")
            else:
                print(f"Command: {res['command']}")


def handle_ai(engine: CortexEngine, topic: str, force_llm: bool = False):
    info = engine.explain_ai_concept(topic, force_llm=force_llm)
    print(f"\n{MAGENTA}{BOLD}🧠 {info.get('title', 'AI Guide')}{RESET}")
    print(f"{DIM}Paradigm: {info.get('paradigm', 'Artificial Intelligence')} | Source: {info.get('source', 'Cortex')}{RESET}\n")

    if "layman_guide" in info:
        print(f"{BOLD}🎮 1. Layman & Point-and-Click Guide (Synapse Studio):{RESET}")
        print(f"  {info['layman_guide']}\n")
    elif "summary" in info:
        print(f"{BOLD}Overview:{RESET}")
        print(f"  {info['summary']}\n")

    if "math_and_theory" in info:
        print(f"{BOLD}📐 2. Core Math & Algorithmic Theory:{RESET}")
        for line in info["math_and_theory"].splitlines():
            print(f"  {line}")
        print()

    if "hyperparameters" in info and isinstance(info["hyperparameters"], dict):
        print(f"{BOLD}🎛️  3. Key Variables & Hyperparameter Tuning:{RESET}")
        for param, details in info["hyperparameters"].items():
            if isinstance(details, dict):
                print(f"  • {GREEN}{param}{RESET} (Recommended: {YELLOW}{details.get('recommended', 'N/A')}{RESET})")
                print(f"    {details.get('desc', '')} -> {DIM}{details.get('effect', '')}{RESET}")
            else:
                print(f"  • {GREEN}{param}:{RESET} {details}")
        print()

    if "code_template" in info:
        print(f"{BOLD}💻 4. Minimal Runnable Python Template:{RESET}")
        for line in info["code_template"].splitlines():
            print(f"  {CYAN}{line}{RESET}")
        print()

    if "debugging_tips" in info:
        print(f"{BOLD}🛠️  5. Debugging & Potato CPU Optimization:{RESET}")
        for line in info["debugging_tips"].splitlines():
            print(f"  {YELLOW}{line}{RESET}")
        print()


def handle_forge(rebuild: bool = False, verify: bool = False, train: bool = False):
    forge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "forge"))
    if rebuild:
        print(f"{CYAN}[*] Rebuilding SQLite FTS5 Knowledge Base and Phi-3 Dataset...{RESET}")
        subprocess.run([sys.executable, os.path.join(forge_dir, "build_kb.py")], check=True)
        subprocess.run([sys.executable, os.path.join(forge_dir, "build_dataset.py")], check=True)
        if shutil.which("ollama"):
            print(f"{CYAN}[*] Compiling `cortex-phi3:latest` in Ollama...{RESET}")
            subprocess.run(["ollama", "create", "cortex-phi3", "-f", os.path.join(forge_dir, "Modelfile.phi3")], check=True)
    if verify or not (rebuild or train):
        subprocess.run([sys.executable, os.path.join(forge_dir, "train_phi3_qlora.py"), "--verify-config"], check=True)
    if train:
        subprocess.run([sys.executable, os.path.join(forge_dir, "train_phi3_qlora.py"), "--train"], check=True)


def print_shell_init():
    hook = """
# --- SynapseOS Cortex Assistant Shell Hook ---
??() {
    if [ -z "$*" ]; then
        cortex --help
    else
        cortex cmd "$*"
    fi
}
?ai() {
    if [ -z "$*" ]; then
        cortex ai neat
    else
        cortex ai "$*"
    fi
}
# ---------------------------------------------
"""
    print(hook.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Cortex: Potato-Grade Linux Guide & AI Experimentation Mentor (cortex-phi3)",
        add_help=True
    )
    parser.add_argument("--potato", action="store_true", help="Force strict potato memory & speed mode")
    subparsers = parser.add_subparsers(dest="subcommand")

    # Command help
    cmd_parser = subparsers.add_parser("cmd", help="Ask for a Linux command and instructions")
    cmd_parser.add_argument("query", nargs="+", help="What task or command you need help with")
    cmd_parser.add_argument("-y", "--yes", "--run", "-x", "--exec", dest="yes", action="store_true", help="Auto-run the suggested command")
    cmd_parser.add_argument("--llm", action="store_true", help="Force live cortex-phi3 synthesis with FTS5 RAG")

    # AI guidance
    ai_parser = subparsers.add_parser("ai", help="Consult AI experimentation mentor (NEAT, RL, PyTorch, SLMs)")
    ai_parser.add_argument("topic", nargs="+", help="AI topic, algorithm, or debugging question")
    ai_parser.add_argument("--llm", action="store_true", help="Force live cortex-phi3 deep-dive generation")

    # Conversational chat
    chat_parser = subparsers.add_parser("chat", help="Ask Lumi (Cortex-Phi3 Socratic Tutor) a question")
    chat_parser.add_argument("message", nargs="+", help="Question or message for Lumi")

    # Forge management
    forge_parser = subparsers.add_parser("forge", help="Manage Phi-3 Mini fine-tuning dataset, FTS5 KB, and QLoRA")
    forge_parser.add_argument("--rebuild", action="store_true", help="Rebuild FTS5 KB, dataset, and cortex-phi3 Ollama model")
    forge_parser.add_argument("--verify", action="store_true", help="Verify Phi-3 QLoRA dataset & target modules")
    forge_parser.add_argument("--train", action="store_true", help="Launch PyTorch PEFT QLoRA training")

    # System status
    subparsers.add_parser("sys", help="Show system hardware, potato budget, FTS5 KB, and cortex-phi3 status")

    # BuildbitOS 1.58-Bit Ternary & PRIME-Moment Attention Potato Benchmark
    subparsers.add_parser("trit", help="Run BuildbitOS 1.58-Bit Ternary POPCNT + PRIME-Moment Attention Potato Benchmark")

    # Shell hook
    subparsers.add_parser("init-shell", help="Generate shell functions for '??' and '?ai'")

    args = parser.parse_args()
    engine = CortexEngine(potato_mode=args.potato)

    if not args.subcommand:
        print_banner()
        handle_sys(engine)
        print(f"{BOLD}Quick Examples:{RESET}")
        print(f"  {CYAN}cortex chat \"how do thrusters help land a rocket?\"{RESET}")
        print(f"  {CYAN}cortex cmd \"boost ram on a potato with zram\"{RESET}")
        print(f"  {CYAN}cortex ai \"neat moon lander\"{RESET}")
        print(f"  {CYAN}cortex trit{RESET}")
        print(f"  {CYAN}cortex forge --verify{RESET}\n")
        return

    if args.subcommand == "sys":
        handle_sys(engine)
    elif args.subcommand == "trit":
        from workbench.labs.c_sim_bridge import benchmark_buildbit_potato_kernels
        res = benchmark_buildbit_potato_kernels(dim=1024, n_tokens=64)
        print(f"\n{CYAN}{BOLD}⚡ BuildbitOS 1.58-Bit Ternary + PRIME-Moment Attention Potato Benchmark:{RESET}")
        if res.get("available"):
            print(f"  {BOLD}1. 1.58-Bit Ternary Bit-Sliced POPCNT Linear Projections ({res['dim']}x{res['dim']}, {res['n_tokens']} tokens):{RESET}")
            print(f"     • Standard FP32 GEMV : {YELLOW}{res['fp32_ms']} ms{RESET} (16x RAM)")
            print(f"     • BuildbitOS trit64  : {GREEN}{res['trit_ms']} ms{RESET} (2 bits/weight, 0 FP muls)")
            print(f"     • Potato CPU Speedup : {GREEN}{BOLD}{res['trit_speedup']}x faster{RESET} (Exact Match: {res['trit_exact_match']})")
            print(f"  {BOLD}2. PRIME-Moment O(D^2) KV-Cache-Free Attention (8 heads x 64 dim, 512 tokens):{RESET}")
            print(f"     • Step Latency       : {GREEN}{res['prime_step_ms']} ms{RESET} ({GREEN}{BOLD}{res['prime_tok_per_sec']} tok/s{RESET})")
            print(f"     • S0/S1/S2 State RAM : {CYAN}{res['prime_state_kb']} KB{RESET} (100% L2 Cache Resident, 0 KV-Cache growth)\n")
        else:
            print(f"  {RED}libsynapse_core.so not loaded; run 'make -C cortex/c_prime shared'{RESET}\n")

    elif args.subcommand == "chat":
        msg_str = " ".join(args.message)
        res = engine.chat_with_cortex(msg_str)
        print(f"\n{CYAN}{BOLD}🤖 Lumi ({res['source']}):{RESET}")
        print(f"  {GREEN}{res['reply']}{RESET}\n")
    elif args.subcommand == "cmd":
        query_str = " ".join(args.query)
        handle_cmd(engine, query_str, auto_exec=args.yes, force_llm=args.llm)
    elif args.subcommand == "ai":
        topic_str = " ".join(args.topic)
        handle_ai(engine, topic_str, force_llm=args.llm)
    elif args.subcommand == "forge":
        handle_forge(rebuild=args.rebuild, verify=args.verify, train=args.train)
    elif args.subcommand == "init-shell":
        print_shell_init()


if __name__ == "__main__":
    main()

