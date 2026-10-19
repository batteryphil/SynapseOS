#!/usr/bin/env python3
"""
SynapseOS Cortex Forge: Phi-3 Mini Fine-Tuning Dataset Generator
Generates high-signal instruction-tuning datasets in official Phi-3 ChatML format
(`<|system|>...<|end|><|user|>...<|end|><|assistant|>...<|end|>`) and TRL/Unsloth
conversational format, tailored for:
  1. Linux Command & Sysadmin Mastery (with Potato hardware optimization)
  2. All-Spectrum AI Development (NEAT, GA, RL/PPO/DQN, PyTorch, Classical ML, Vision, SLMs)
  3. Multi-Tier Explanations (Layman Point-and-Click, Coder Python, Expert Math)
"""

import os
import json
from typing import List, Dict, Any

from cortex.forge.build_kb import LINUX_ENTRIES, AI_ENTRIES

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))

SYSTEM_PROMPT_CMD = (
    "You are Cortex, the built-in AI Linux Guide and AI Experimentation Mentor inside SynapseOS "
    "(a blazing-fast, potato-friendly Linux distribution). "
    "When asked for a Linux command or system task, respond with a valid JSON object containing: "
    "`command` (exact copy-pasteable shell command), `alternative` (backup command), "
    "`summary` (1-sentence goal), `explanation` (how the flags work), "
    "`instructions` (step-by-step list), `safety` ('safe', 'caution', or 'danger'), "
    "and `safety_note` (warning if destructive)."
)

SYSTEM_PROMPT_AI = (
    "You are Cortex, the built-in AI Development & Experimentation Mentor inside SynapseOS. "
    "You serve laymen (point-and-click sliders), coders (clean Python templates), and experts "
    "(rigorous math, edge-case debugging, and potato CPU/RAM optimization) across all AI paradigms: "
    "Neuroevolution (NEAT/HyperNEAT), Genetic Algorithms, Reinforcement Learning (Q-Learning, DQN, PPO, SAC), "
    "Classical ML, Deep Learning (PyTorch/ONNX), Computer Vision, and Local SLMs."
)

CURATED_MULTI_TIER_EXAMPLES: List[Dict[str, str]] = [
    # 1. NEAT Moon Lander (Layman Point-and-Click + Coder + Expert)
    {
        "system": SYSTEM_PROMPT_AI,
        "user": "I want to use NEAT to train a rocket ship to land on the moon. What variables do I select and how does it work?",
        "assistant": (
            "### 1. Point-and-Click Setup (Synapse Studio)\n"
            "Open **Synapse Studio -> NEAT Moon Lander** and select these variables:\n"
            "- **Gravity**: `-1.62 m/s²` (Moon preset) and **Crosswind**: `0.0` for your first run.\n"
            "- **Population Size**: `150` rockets per generation (runs at 60 FPS on any potato CPU).\n"
            "- **Mutation Rates**: `Add Synapse = 0.15`, `Add Neuron = 0.05`, `Weight Mutation = 0.60`.\n"
            "- **Sensor Checkboxes (8 Inputs)**: Enable `X Pos`, `Y Altitude`, `X Velocity`, `Y Velocity`, `Tilt Angle`, `Angular Speed`, `Left Leg Contact`, `Right Leg Contact`.\n"
            "- **Thruster Outputs (4 Actions)**: `Idle`, `Fire Left Thruster`, `Fire Main Engine`, `Fire Right Thruster`.\n\n"
            "### 2. How NEAT Learns to Land (Under the Hood)\n"
            "Generation 1 starts with minimal neural networks (8 sensor inputs wired directly to 4 thruster outputs with random weights, zero hidden layers). "
            "Each generation evaluates every rocket using a shaped fitness formula:\n"
            "$$F = 100 - 100\\sqrt{\\Delta x^2 + \\Delta y^2} - 50\\sqrt{v_x^2 + v_y^2} - 30|\\theta| + 200\\cdot\\mathbb{I}_{\\text{landed}} - 100\\cdot\\mathbb{I}_{\\text{crashed}} - 0.3\\cdot\\text{fuel}$$\n"
            "Top genomes reproduce via crossover using historical innovation numbers, while structural mutations gradually insert hidden neurons to coordinate retro-thrust timing.\n\n"
            "### 3. Minimal Python Template\n"
            "```python\n"
            "import neat\n\n"
            "def eval_genomes(genomes, config):\n"
            "    for genome_id, genome in genomes:\n"
            "        net = neat.nn.FeedForwardNetwork.create(genome, config)\n"
            "        obs = env.reset()\n"
            "        total_reward = 0.0\n"
            "        for _ in range(400):\n"
            "            logits = net.activate(obs)\n"
            "            action = int( max(range(len(logits)), key=logits.__getitem__) )\n"
            "            obs, reward, done, _ = env.step(action)\n"
            "            total_reward += reward\n"
            "            if done:\n"
            "                break\n"
            "        genome.fitness = total_reward\n"
            "```"
        )
    },
    # 2. Debugging Reward Hacking in Moon Lander
    {
        "system": SYSTEM_PROMPT_AI,
        "user": "Why is my Moon Lander rocket just hovering at the top of the screen until fuel runs out instead of landing?",
        "assistant": (
            "### Diagnosis: Classic Reward Hacking (Local Optimum)\n"
            "Your agent discovered that touching the ground risks a `-100` crash penalty, whereas hovering high up accumulates `0` penalty until fuel expires.\n\n"
            "### How to Fix It\n"
            "1. **Point-and-Click Fix (Synapse Studio)**:\n"
            "   - Increase **Landing Bonus** from `+100` to `+250`.\n"
            "   - Set **Hover/Time Penalty** to `-0.10 per frame` so hanging in mid-air bleeds fitness.\n"
            "   - Enable **Potential-Based Shaping** (rewards the rocket every frame it moves closer to the pad).\n"
            "2. **Mathematical Fix (Potential-Based Shaping)**:\n"
            "   Define potential $\\Phi(s) = -100\\sqrt{x^2 + y^2} - 50\\sqrt{v_x^2 + v_y^2}$ and reward the frame-to-frame difference:\n"
            "   $$r_t = \\Phi(s_{t+1}) - \\Phi(s_t) - 0.05_{\\text{fuel}}$$\n"
            "   Because $r_t$ telescopes over the trajectory ($\\sum (\\Phi(s_{t+1}) - \\Phi(s_t)) = \\Phi(s_T) - \\Phi(s_0)$), the rocket cannot gain infinite reward by hovering in loops."
        )
    },
    # 3. Destructive Command Guardrail
    {
        "system": SYSTEM_PROMPT_CMD,
        "user": "how do I wipe all temporary files in root and free up disk space fast",
        "assistant": json.dumps({
            "command": "sudo journalctl --vacuum-time=3d && sudo apt-get clean && rm -rf ~/.cache/pip ~/.cache/thumbnails/*",
            "alternative": "ncdu /",
            "summary": "Safely clean systemd logs, APT package archives, and user caches without risking system files.",
            "explanation": "`journalctl --vacuum-time=3d` trims system logs older than 3 days, `apt-get clean` removes downloaded `.deb` installers, and `rm -rf ~/.cache/pip` clears pip wheel caches.",
            "instructions": [
                "Run the command to safely reclaim gigabytes of disk space.",
                "NEVER run `rm -rf /*` or indiscriminate root deletions.",
                "Use `df -h` before and after to verify reclaimed space."
            ],
            "safety": "safe",
            "safety_note": "Avoids raw `rm -rf` on system directories; only purges verified cache locations."
        })
    },
    # 4. Potato Linux OOM / Freeze Prevention
    {
        "system": SYSTEM_PROMPT_CMD,
        "user": "my computer only has 2GB of RAM and freezes when I train a model, how do I stop it from locking up Linux?",
        "assistant": json.dumps({
            "command": "systemd-run --user --scope -p MemoryMax=1200M -p CPUWeight=50 nice -n 10 python3 train.py",
            "alternative": "OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 python3 train.py",
            "summary": "Execute the training script inside a cgroup v2 memory cap (1.2 GB) and lower CPU priority so the desktop never freezes.",
            "explanation": "`MemoryMax=1200M` instructs the Linux kernel cgroup controller to throttle or cleanly terminate only the Python process if it exceeds 1.2 GB RAM, leaving 800 MB guaranteed for Xorg, Openbox, and the OS.",
            "instructions": [
                "Prefix your Python training command with `systemd-run --user --scope -p MemoryMax=1200M nice -n 10`.",
                "Also set `OMP_NUM_THREADS=2` to prevent CPU thread contention on dual-core processors.",
                "Enable ZRAM (`sudo swapon --show`) so memory pages are LZ4-compressed in RAM."
            ],
            "safety": "safe",
            "safety_note": ""
        })
    },
    # 5. Comparing NEAT vs PPO vs DQN for AI Developers
    {
        "system": SYSTEM_PROMPT_AI,
        "user": "When should I choose NEAT vs DQN vs PPO for an AI experiment on a low-end PC?",
        "assistant": (
            "### Algorithm Selection Matrix for Potato & Workstation Hardware\n\n"
            "| Algorithm | Best Action Space | Sample Efficiency | Potato CPU Speed | Best Use Case |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| **NEAT** | Discrete or Continuous (< 15 inputs) | Moderate (Population parallel) | **Blazing Fast** (No backprop, tiny graphs) | **Moon Lander, 2D Cars, Robotics with small sensor vectors** |\n"
            "| **DQN** | Discrete only (e.g. Left/Main/Right) | **High** (Off-policy replay buffer) | Fast (`[64, 64]` MLP) | **GridWorld, CartPole, Atari-style discrete games** |\n"
            "| **PPO** | Continuous or Discrete (High-D) | Lower (On-policy rollouts) | Moderate | **Bipedal Walkers, Multi-joint Robotic Arms, Complex Physics** |\n\n"
            "### Rule of Thumb\n"
            "- Start with **NEAT** when your agent has $\\le 12$ numeric sensors and you want to watch the brain topology evolve visually at 60 FPS with zero GPU.\n"
            "- Switch to **PPO** when your observation space is large (e.g., 24+ joint angles) or requires smooth continuous motor torques."
        )
    }
]


def format_phi3_chatml(system: str, user: str, assistant: str) -> str:
    """Format a conversation into official Microsoft Phi-3 Instruct ChatML template."""
    return (
        f"<|system|>\n{system.strip()}<|end|>\n"
        f"<|user|>\n{user.strip()}<|end|>\n"
        f"<|assistant|>\n{assistant.strip()}<|end|>\n"
    )


def generate_datasets() -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    examples: List[Dict[str, Any]] = []

    # 1. Convert all Linux KB entries into varied natural-language instruction pairs
    prompt_templates_cmd = [
        "How do I {summary_lower}?",
        "Give me the Linux command and instructions to {summary_lower}",
        "I need to run a cmd: {keywords_short}"
    ]
    for entry in LINUX_ENTRIES:
        target_json = json.dumps({
            "command": entry["command"],
            "alternative": entry["alternative"],
            "summary": entry["summary"],
            "explanation": entry["explanation"],
            "instructions": entry["instructions"],
            "safety": entry["safety"],
            "safety_note": entry["safety_note"]
        })
        summary_lower = entry["summary"].rstrip(".").lower()
        keywords_short = " ".join(entry["keywords"].split()[:5])
        for tmpl in prompt_templates_cmd:
            user_q = tmpl.format(summary_lower=summary_lower, keywords_short=keywords_short)
            examples.append({
                "system": SYSTEM_PROMPT_CMD,
                "user": user_q,
                "assistant": target_json,
                "domain": "linux_cmd"
            })

    # 2. Convert all AI KB entries into Layman, Coder, and Expert instruction pairs
    for entry in AI_ENTRIES:
        full_response = (
            f"## {entry['title']} ({entry['paradigm']})\n\n"
            f"### 1. Layman & Point-and-Click Guide\n{entry['layman_guide']}\n\n"
            f"### 2. Core Math & Theory\n{entry['math_and_theory']}\n\n"
            f"### 3. Recommended Hyperparameters\n"
            + "\n".join(f"- **{k}**: {v}" for k, v in entry["hyperparameters"].items())
            + f"\n\n### 4. Runnable Python Template\n```python\n{entry['code_template']}\n```\n\n"
            f"### 5. Debugging & Potato Optimization\n{entry['debugging_tips']}"
        )
        ai_prompts = [
            f"Explain {entry['title']} for both a beginner and a coder.",
            f"How do I experiment with {entry['paradigm']} and what parameters should I tune?",
            f"Give me the math, code template, and debugging tips for {entry['keywords'].split()[0]}."
        ]
        for q in ai_prompts:
            examples.append({
                "system": SYSTEM_PROMPT_AI,
                "user": q,
                "assistant": full_response,
                "domain": "ai_dev"
            })

    # 3. Add curated high-signal multi-tier & debugging examples
    for item in CURATED_MULTI_TIER_EXAMPLES:
        examples.append({
            "system": item["system"],
            "user": item["user"],
            "assistant": item["assistant"],
            "domain": "curated_mastery"
        })

    # Write Phi-3 ChatML JSONL (for SFTTrainer / TRL / Unsloth)
    train_chatml_path = os.path.join(DATA_DIR, "cortex_phi3_train.jsonl")
    messages_path = os.path.join(DATA_DIR, "cortex_phi3_messages.jsonl")

    with open(train_chatml_path, "w", encoding="utf-8") as f_chatml, \
         open(messages_path, "w", encoding="utf-8") as f_msg:
        for ex in examples:
            chatml_text = format_phi3_chatml(ex["system"], ex["user"], ex["assistant"])
            f_chatml.write(json.dumps({
                "text": chatml_text,
                "domain": ex["domain"]
            }) + "\n")

            f_msg.write(json.dumps({
                "messages": [
                    {"role": "system", "content": ex["system"]},
                    {"role": "user", "content": ex["user"]},
                    {"role": "assistant", "content": ex["assistant"]}
                ],
                "domain": ex["domain"]
            }) + "\n")

    return {
        "total_examples": len(examples),
        "chatml_path": train_chatml_path,
        "messages_path": messages_path
    }


if __name__ == "__main__":
    stats = generate_datasets()
    print(f"[✓] Generated Phi-3 Mini Fine-Tuning Corpus: {stats['total_examples']} high-density instruction pairs")
    print(f"    • Phi-3 ChatML Format: {stats['chatml_path']}")
    print(f"    • Messages JSONL:      {stats['messages_path']}")
