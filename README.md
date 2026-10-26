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

## 1. Download & Boot SynapseOS (Full LLM ISO or Fast Lite ISO)

### Option A: Full Bootable ISO With Fine-Tuned `cortex-phi3` LLM Built In (`2.6 GB`)
Includes **everything 100% offline**: Debian 12 + Openbox + the fine-tuned **`cortex-phi3:latest` LLM (`2.2 GB` GGUF)** + Ollama daemon + C99 `prime-moment` engine + 7 AI Labs + all **325 K–12 lessons** + offline `espeak-ng` Read-Aloud TTS.

```bash
# 1. Clone repo
git clone https://github.com/batteryphil/SynapseOS.git
cd SynapseOS

# 2. Download, reassemble, SHA256-verify, and boot the Full 2.6 GB LLM ISO in QEMU (1 command):
./scripts/download_and_boot_full_iso.sh

# Or download & verify the .iso file only (to flash to a USB stick or attach in VirtualBox/VMware):
./scripts/download_and_boot_full_iso.sh --download
```

### Option B: Boot the Compressed Lite ISO Directly From This Git Repo (`~400 MB`, No LLM)
The repository also tracks the **Lite Experimentation ISO** (`SynapseOS-Lite-x86_64.iso`, excluding the `2.2 GB` LLM weights) inside [`iso/`](file:///home/phil/.gemini/antigravity/scratch/synapse-os/iso) so every file stays under GitHub's `100 MB` per-file `git push` limit.

```bash
# Recombine, decompress, and SHA256-verify SynapseOS-Lite-x86_64.iso
./iso/decompress_iso.sh

# Boot in QEMU/KVM
qemu-system-x86_64 -enable-kvm -m 2048 -smp 2 -cdrom iso/SynapseOS-Lite-x86_64.iso
```

| ISO Artifact | Uncompressed Rootfs | SquashFS | Bootable `.iso` Size | How to Run | Contents |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`SynapseOS-Debian12-Potato-x86_64.iso`** (**Full LLM**) | `3,998.0 MB` | `2,546.1 MB` (`zstd`) | **`2.6 GB`** | `./scripts/download_and_boot_full_iso.sh` (GitHub Release `v1.0-k12`) | Everything in Lite + pre-baked `2.2 GB` `cortex-phi3:latest` GGUF + Ollama runtime + `espeak-ng` TTS |
| **`SynapseOS-Lite-x86_64.iso`** (In Repo `iso/`) | `1,420.0 MB` | `345.0 MB` (`xz -Xbcj x86`) | **`~405 MB`** | `./iso/decompress_iso.sh` (In-Repo) | Debian 12 + Openbox + 7 AI Labs + 325 K–12 Lessons + `cortex_kb.sqlite` + C99 `prime-moment` (`libprime.so`) |

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

# Browse & manage the Complete K-12 Rolling Curriculum (Kindergarten + Grades 1-12)
./synapse pack list-years
./synapse pack set-year K            # Install Kindergarten (year_00)
./synapse pack set-year 1            # Install Grade 1 (year_01), wipes old year files, keeps Transcript
./synapse curriculum y00_math        # Run Kindergarten Math + AI Lab
./synapse curriculum y08_science_q2  # Run Grade 8 Science Quarter 2 (Winter Unit) + AI Lab
./synapse pack advance-year          # Graduate to next School Year (wipes old year, saves Report Card)

# Run all automated unit & integration tests
python3 -m unittest discover -s tests
```

---

## 4. Complete K–12 Rolling Year-by-Year School Curriculum (`curricula/year_00.json` – `year_12.json`)

Every grade from **Kindergarten (`year_00` / Grade K)** through **Grade 12 (`year_12` / Senior Capstone)** (**13 complete grades**) includes **5 Full-Year Subject Courses** + **20 Quarterly Unit Lessons (`Q1 Fall`, `Q2 Winter`, `Q3 Spring`, `Q4 Capstone`)** = **325 total K–12 lessons** + **91 bilingual `EN`/`FR` visual levels**:
1. **📐 Mathematics** (*Counting & Shapes $\rightarrow$ Arithmetic $\rightarrow$ Fractions/Ratios $\rightarrow$ Algebra & Geometry $\rightarrow$ Pre-Calculus, Calculus & Linear Algebra*)
2. **🔬 Science** (*5 Senses & Weather $\rightarrow$ Forces & Ecosystems $\rightarrow$ Genetics, Waves & Chemistry $\rightarrow$ Physics, Thermodynamics & Computational Neuroscience*)
3. **📖 Reading & Language Arts (ELA)** (*Alphabet Phonics $\rightarrow$ Reading Comprehension & Grammar $\rightarrow$ Claim-Evidence-Reasoning (CER) $\rightarrow$ Rhetoric & Technical Peer Review*)
4. **🌍 Social Studies & History** (*Classroom Civics & Maps $\rightarrow$ Ancient Civilizations & U.S./World History $\rightarrow$ Constitution & Economics $\rightarrow$ AI Ethics, Public Policy & TCO*)
5. **🤖 Connected AI & Coding Assignment** (*Hands-on simulation + auto-graded Python worksheet tied directly to that grade's Math, Science, ELA, and History lessons*)

Every lesson contains **6 Complete Textbook Sections**:
- **Section 1**: Core Textbook Lesson & National Standards Alignment (`CCSS Math`, `NGSS Science`, `CCSS ELA`, `NCSS C3`, `CSTA CS`)
- **Section 2**: Full 36-Week / 4-Quarter Course Syllabus (`Q1 Weeks 1–9`, `Q2 Weeks 10–18`, `Q3 Weeks 19–27`, `Q4 Weeks 28–36`)
- **Section 3**: Academic Vocabulary Glossary (Terms & Definitions)
- **Section 4**: Step-by-Step Worked Textbook Examples
- **Section 5**: Traditional Practice Worksheet & Self-Check Quiz (with Answer Key)
- **Section 6**: Teacher Guide & 100-Point Mastery Rubric (`40 pts Core Subject + 30 pts Quiz + 30 pts AI Lab & Python Code`)

- **1-Year-at-a-Time Potato Storage Wiper**: Only **one** school year's curriculum package resides in active classroom storage (`~/.config/synapse-os/active_pack/current_pack.json`). Advancing a student (`./synapse pack advance-year` or clicking **`★ Yr X ↻`** in the Teacher Report tab) **wipes the old year's pack and scratch files** while **permanently preserving the student's Cumulative Multi-Subject Report Card Transcript, Gold Trophies, Coins, and High Scores** in `student_profile.json`.

---

## 5. Repository Structure

```text
synapse-os/
├── synapse                                # Unified CLI entrypoint
├── SYNAPSE_OS_SPECS.txt                   # Full technical architecture & benchmark specification
├── curricula/
│   ├── index.json                         # Master manifest of all 13 K-12 School Year Curricula (K-12)
│   └── year_00.json .. year_12.json       # Hosted Kindergarten + Grades 1-12 complete textbook packages
├── bin/
│   ├── synapse-studio                     # Studio desktop launcher
│   └── synapse-tunnel                     # Encrypted HTTPS noVNC + Cloudflare remote classroom tunnel
├── iso/
│   ├── SynapseOS-Lite-x86_64.iso.zst.part-* # 5 chunks (<90 MB each, 374 MB total) of the 385 MB Lite ISO
│   ├── SynapseOS-Lite-x86_64.iso.sha256   # SHA256 checksum for verification
│   └── decompress_iso.sh                  # 1-command ISO reassembly + zstd decompression + SHA256 check
├── cortex/
│   ├── engine.py                          # Three-tier AI engine (FTS5 + C99 PRIME Moment + Ollama + Safety Shield)
│   ├── prime_window.py                    # ctypes binding to libprime.so + O(W+K) context compressor
│   ├── c_prime/                           # Native C99 PRIME-Moment & Sim kernels (GCC + Cosmopolitan + Fil-C)
│   ├── knowledge/cortex_kb.sqlite         # 92 KB SQLite FTS5 BM25 database
│   └── forge/
│       ├── Modelfile.phi3                 # Fast-TTFT (num_ctx=1024) Ollama Modelfile
│       ├── cortex_phi3_train.jsonl        # Curated instruction-tuning dataset
│       ├── hybrid_prime_attention.py      # PyTorch causal-mask Transformer surgery for Phi-3 & Qwen2
│       └── train_phi3_qlora.py            # 4-bit NF4 QLoRA trainer with GPU hardware guardrail
├── workbench/
│   ├── studio_gui.py                      # GTK3 + Cairo 60 FPS 7-Lab GUI + K-12 Teacher Report Card
│   ├── kid_arcade_view.py                 # Full-screen Synapse Kids gamified view (EN/FR toggle)
│   ├── k12_curricula.py                   # 12-Year K-12 Traditional Subjects + AI Curriculum generator
│   ├── pack_manager.py                    # 1-Year-at-a-Time Wiper & Persistent Student Transcript Vault
│   ├── labs/prime_attention_lab.py        # Lab 7: Interactive O(N^2) vs O(W+K) PRIME Moment simulator
│   ├── curriculum.py                      # 35 Lab Examples (5 per lab) & classroom missions
│   └── sandbox_runner.py                  # Subprocess Python sandbox (8s timeout)
├── distro/
│   └── build-iso.sh                       # Debian 12 Live ISO builder (--lite for 385 MB, --all for 2.5 GB)
└── tests/                                 # Automated unit & integration test suite (32 tests)
```
