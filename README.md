# SynapseOS: Potato-Grade Linux Distro & 7-Lab Native AI Workbench

- **Base OS**: Debian 12 Bookworm (`minbase`, `x86_64`) + Xorg + Openbox + Tint2 + `tty1` autologin (`242 MB` live idle RAM).
- **Synapse Studio & Synapse Kids Arcade**: Native GTK3 + Cairo 60 FPS AI Workbench (`62.9 MB` full runtime RSS, `3.27 ms/frame` at `1280x720`, `0 KB` texture bloat, `0.09s` cold start) featuring:
  - **Full-Screen `Synapse Kids` Mode** ([`workbench/kid_arcade_view.py`](file:///home/phil/.gemini/antigravity/scratch/synapse-os/workbench/kid_arcade_view.py)): Gamified Scratch-style classroom UI with 1-click **`L1`–`L7` Level Selector Pills**, interactive canvas clicks across all 7 levels, `NEAT Moon Lander` solar panels/callouts & Lunar Landing Pad touchdown physics, live swirling 2D `Color Sorter Brain`, waving `Cortex-Phi3` Robot Mascot + Speech Bubble, live mission checkboxes, 3-star scoring, and 1-click **English / French (`EN ▸ FR`)** toggle.
  - **`⚙ Teacher / Pro Workstation Mode`** ([`workbench/studio_gui.py`](file:///home/phil/.gemini/antigravity/scratch/synapse-os/workbench/studio_gui.py)): Full 3-column engineering interface with **35 curated Lab Examples (`5 per lab`)**, **14 Classroom Tutorials**, **Direct Structural Brain Surgery (`+ / - Neurons & Synapses`)**, live **FPS / PRIME C99 tok/s / Phi-3 tok/s & TTFT / RAM telemetry**, **60 FPS Animated Phi-3 + PRIME Brain Visualizer**, **General Chat Mode**, **Safe Linux Command Runner**, and **Encrypted Remote Browser Tunnel (`synapse-tunnel`)**.
- **Three-Tier Local AI Engine**:
  1. **Tier 1 (`0.68 ms`, `92 KB`)**: SQLite FTS5 BM25 offline knowledge base (`cortex_kb.sqlite`).
  2. **Tier 2 (`8,737 tok/s` on BC-250 / `6,738 tok/s` potato CPU, `262 KB` constant $\mathcal{O}(1)$ RAM, zero AVX2 required)**: Native C99 **PRIME Moment Sliding-Window Attention** engine (`libprime.so` / `prime-moment`, integrated from [`batteryphil/PRIME-Moment-Attention`](https://github.com/batteryphil/PRIME-Moment-Attention)).
  3. **Tier 3 (`24.8 tok/s` on AMD BC-250 / `11.6 tok/s` 4-core CPU, `2.2 GB`)**: Local `cortex-phi3:latest` (`Phi-3-Mini-4K-Instruct` `Q4_K_M`, `num_ctx=1024`).

---

## 1. Boot the Compressed Lite ISO Directly From This Repo (`385 MB`, No LLM)

The repository includes the complete bootable **Lite Experimentation ISO** (`SynapseOS-Lite-x86_64.iso`, excluding the `2.2 GB` LLM weights) compressed with `xz -Xbcj x86` + `zstd` and split into `< 90 MB` chunks inside [`iso/`](file:///home/phil/.gemini/antigravity/scratch/synapse-os/iso) so every file stays under GitHub's `100 MB` per-file `git push` limit.

```bash
# 1. Clone repo
git clone https://github.com/batteryphil/SynapseOS.git
cd SynapseOS

# 2. Recombine, decompress, and SHA256-verify SynapseOS-Lite-x86_64.iso (385 MB)
./iso/decompress_iso.sh

# 3. Boot in QEMU/KVM
qemu-system-x86_64 -enable-kvm -m 2048 -smp 2 -cdrom iso/SynapseOS-Lite-x86_64.iso
```

| ISO Artifact | Uncompressed Rootfs | SquashFS (`xz -Xbcj x86`) | Bootable `.iso` Size | Repo `.zst.part-*` Total | Contents |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`SynapseOS-Lite-x86_64.iso`** (In Repo `iso/`) | `1,347.9 MB` | `323.9 MB` (`24.6%`) | **`385 MB`** | **`374 MB`** (`4 x 90 MB` + `1 x 14 MB`) | Debian 12 + Openbox + 7 AI Labs + 14 School Lessons + `cortex_kb.sqlite` + C99 `prime-moment` (`libprime.so`) |
| **`SynapseOS-Debian12-Potato-x86_64.iso`** (Full LLM) | `3,540.0 MB` | `2,410.0 MB` | **`2.5 GB`** | Hosted via Release / HF | Everything in Lite + pre-baked `2.2 GB` `cortex-phi3:latest` GGUF + Ollama runtime |

---

## 2. 7 Native GTK3 + Cairo AI Labs (`workbench/`) — 35 Presets (`5 per Lab`)

| Lab | Paradigm | Interactive Parameters & Brain Surgery | Headless CPU Speed (`12 gens`) |
| :--- | :--- | :--- | :--- |
| **1. NEAT Rocket Moon Lander** | Neuroevolution (`NEAT`) | Gravity, Crosswind, Thruster Power, Safe Landing Speed, Pop Size, Add-Neuron/Synapse Rate, Mutation Power, Target Hidden Neurons | `24.1 ms` |
| **2. NEAT Self-Driving Lidar Car** | Autonomous Control (`NEAT`) | Lidar Ray Range, Max Speed, Steering Agility, Track Width, Pop Size, Mutation, Target Hidden Neurons | `189.4 ms` |
| **3. RL Hazard GridWorld** | Tabular RL (`Q-Learning` & `SARSA`) | Learning Rate ($\alpha$), Discount ($\gamma$), Exploration ($\epsilon$), Lava Penalty, Goal Reward, Slippery Wind | `8.2 ms` |
| **4. CartPole Balance** | Neuro-Policy Control | Gravity, Pole Length, Motor Force, Wind Gusts, Pop Size, Mutation Power, Target Hidden Neurons | `31.6 ms` |
| **5. Neural Network Backprop** | Deep Learning (`MLP`) | Dataset (`XOR`, `Circles`, `Moons`, `Spiral`), Hidden Neurons, LR ($\eta$), L2 ($\lambda$), Noise, Batch Steps | `64.5 ms` |
| **6. Predator-Prey Swarm** | Co-Evolutionary Boids | Prey Flock Size, Predator Count, Vision Radius, Max Speeds, Cohesion Drive, Food Density | `42.8 ms` |
| **7. PRIME Moment Attention** | Hybrid Sliding Window + $\mathcal{O}(1)$ C99 Memory | Context Tokens ($N$), Local Window ($W$), PRIME Moments ($K$), EMA Decay ($\gamma$), Recall Temp, Threads | `14.2 ms` (`8,737 tok/s` C99) |

---

## 3. CLI, Remote Browser Tunnel & Test Commands

```bash
# Launch the 7-Lab GTK3 + Cairo AI Workbench GUI (starts in Synapse Kids mode by default; set SYNAPSE_INITIAL_MODE=pro for Teacher Mode)
./synapse studio

# Start encrypted HTTPS Remote Browser Tunnel (noVNC + Cloudflare Quick Tunnel)
./bin/synapse-tunnel synapse-ai

# Run headless benchmark across all 7 AI Labs
./synapse studio --benchmark --gens 12

# Run the native C99 PRIME-Moment O(1) Attention benchmark (10,000 tokens)
./cortex/c_prime/bin/prime

# Query the Three-Tier Cortex Copilot (FTS5 + C99 PRIME Moment + Ollama)
./synapse cortex cmd "compress directory with zstd"
./synapse cortex ai "prime moment attention"

# Rebuild the Lite ISO (385 MB, no LLM) or Full ISO (2.5 GB, with LLM)
./distro/build-iso.sh --lite
./distro/build-iso.sh --all

# Run all automated unit & integration tests
python3 -m unittest discover -s tests
```

---

## 4. Repository Structure

```text
synapse-os/
├── synapse                                # Unified CLI entrypoint
├── SYNAPSE_OS_SPECS.txt                   # Full technical architecture & benchmark specification
├── bin/
│   ├── synapse-studio                     # Studio desktop launcher
│   └── synapse-tunnel                     # Encrypted HTTPS noVNC + Cloudflare remote classroom tunnel
├── iso/
│   ├── SynapseOS-Lite-x86_64.iso.zst.part-* # 5 chunks (<90 MB each, 374 MB total) of the 385 MB Lite ISO
│   ├── SynapseOS-Lite-x86_64.iso.sha256   # SHA256 checksum for verification
│   └── decompress_iso.sh                  # 1-command ISO reassembly + zstd decompression + SHA256 check
├── cortex/
│   ├── engine.py                          # Three-tier AI engine (FTS5 + C99 PRIME Moment + Ollama + General Chat)
│   ├── prime_window.py                    # ctypes binding to libprime.so + O(W+K) context compressor
│   ├── c_prime/                           # Native C99 PRIME-Moment engine (prime + libprime.so)
│   ├── knowledge/cortex_kb.sqlite         # 92 KB SQLite FTS5 BM25 database
│   └── forge/
│       ├── Modelfile.phi3                 # Fast-TTFT (num_ctx=1024) Ollama Modelfile
│       ├── cortex_phi3_train.jsonl        # Curated instruction-tuning dataset
│       ├── hybrid_prime_attention.py      # PyTorch causal-mask Transformer surgery for Phi-3 & Qwen2
│       └── train_phi3_qlora.py            # 4-bit NF4 QLoRA trainer with GPU hardware guardrail
├── workbench/
│   ├── studio_gui.py                      # GTK3 + Cairo 60 FPS 7-Lab GUI + Teacher/Pro Workstation
│   ├── kid_arcade_view.py                 # Full-screen Synapse Kids gamified view (EN/FR toggle)
│   ├── labs/prime_attention_lab.py        # Lab 7: Interactive O(N^2) vs O(W+K) PRIME Moment simulator
│   ├── curriculum.py                      # 35 Lab Examples (5 per lab) & 14 interactive classroom missions
│   └── sandbox_runner.py                  # Subprocess Python sandbox (8s timeout)
├── distro/
│   └── build-iso.sh                       # Debian 12 Live ISO builder (--lite for 385 MB, --all for 2.5 GB)
└── tests/                                 # Automated unit & integration test suite
```
