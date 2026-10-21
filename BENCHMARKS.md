# SynapseOS — Reproducible Engineering & Educational Validation Benchmarks

Every metric claimed in SynapseOS can be reproduced locally in ~12 seconds with a single command:

```bash
./synapse validate --json validation_report.json
```

This suite ([`benchmarks/reproducible_validation.py`](benchmarks/reproducible_validation.py)) separates **runtime resident memory (RSS)** from **on-disk model storage**, **cold startup cost**, **hardware-specific SIMD optimizations vs. portable fallbacks**, **curriculum lesson completion**, **Socratic tutor latency**, and **explicit failure modes** across two reference targets:

1. **Salvaged / Embedded Target**: **AMD BC-250 (`BC08-25010`)** — PlayStation 5 APU mining board (`x86_64`, Kernel `5.15.0`, Python `3.11.2`).
2. **Workstation Reference Target**: **Dell Precision 7920 (`Intel Xeon Gold 6136 @ 3.00GHz`)** — (`x86_64`, Kernel `7.0.0`, Python `3.12.3`).

---

## 1. Runtime Memory vs. Model Storage Separation

A common pitfall in local AI benchmarks is conflating GUI/simulation process RAM with external LLM daemon weights or disk assets. Below is the strict separation measured from `/proc/<pid>/status`:

| Component / Tier | Runtime Resident RAM (`VmRSS`) | Disk Storage Footprint | Notes |
| :--- | :--- | :--- | :--- |
| **Synapse Studio Headless Suite (All 7 AI Labs + C99 PRIME)** | **`24.9 MB – 27.0 MB`** *(Peak `33.6 MB`)* | `~310 KB` (Python + C99 `.so`) | Runs all 7 physics/RL/NEAT engines headlessly |
| **Synapse Studio Live GTK3 + Cairo GUI (Cold Launch)** | **`57.5 MB`** (`58,880 KB`) | **`0 KB` bitmap textures** | 100% procedural Cairo vector rendering at 60 FPS |
| **Synapse Studio Live GTK3 + Cairo GUI (16-Hour Soak Test)** | **`72.1 MB`** (`73,840 KB`) | **`0 KB` bitmap textures** | Measured after 16+ hours (`~3.4M frames`) of continuous 60 FPS evolution |
| **PRIME C99 Second-Order Moment State (`8H, D=64`)** | **`67.1 KB` (`262.0 KB` w/ full buffers)** | **`24.02 KB`** (`libprime.so`) | Constant $O(1)$ L2-cache state vs. **`536.87 MB`** standard Transformer KV-cache at $N=4096$ |
| **Tier-1 Offline Socratic Tutor + SQLite FTS5 BM25 KB** | **`< 1.8 MB`** *(included in process RSS)* | **`96.0 KB`** (`cortex_kb.sqlite`) | **`0 MB` neural weights**; deterministic Socratic hint & BM25 retrieval engine |
| **Active Curriculum Learning Pack (`pack_1` / `pack_2`)** | **`< 64 KB`** *(in-memory dict)* | **`7.38 KB`** JSON | Hot-swapping packs purges old pack files to preserve disk space |
| **Tier-2 Optional Local SLM (`Ollama cortex-phi3` Q4_K_M)** | **`~2.35 GB`** *(separate `ollama` daemon)* | **`2.20 GB`** GGUF on disk | Optional; automatically bypassed in `< 1.1 ms` on low-RAM / potato systems |

---

## 2. Cold Startup Cost Breakdown (`t0 -> Ready`)

Measured via `time.perf_counter()` from process start with cold module imports:

| Subsystem Initialization Stage | AMD BC-250 (`BC08-25010`) | Intel Xeon Gold 6136 |
| :--- | :--- | :--- |
| **1. C99 PRIME Shared Library (`ctypes` + state alloc)** | `67.90 ms` | `88.39 ms` |
| **2. Cortex Engine + SQLite FTS5 Knowledge Base** | `49.13 ms` | `63.62 ms` |
| **3. All 7 AI Lab Physics & Neural Engines Cold Init** | `74.39 ms` | `113.41 ms` |
| **4. Learning Pack Manager + Student Profile Load** | `6.96 ms` | `0.89 ms` |
| **Total Headless Cold Start (`t0 -> All 7 Labs Ready`)** | **`198.38 ms`** | **`266.31 ms`** |

---

## 3. Hardware-Specific Optimizations vs. Portable Baselines

To separate hardware-specific compiler/SIMD optimizations from algorithmic efficiency, `./synapse validate` benchmarks the exact same second-order PRIME Moment recurrence across three execution tiers (`8 heads, D=64`):

| Execution Tier | Compiler / Runtime Flags | AMD BC-250 (`tok/s`) | Xeon Gold 6136 (`tok/s`) | Speedup vs. Pure Python |
| :--- | :--- | :--- | :--- | :--- |
| **Tier A: Hardware-Optimized C99** | `gcc -O3 -march=native -ffast-math` (`libprime.so`) | **`7,707 tok/s`** | **`5,747 tok/s`** | **`5.7x`** (BC-250) / **`4.5x`** (Xeon) |
| **Tier B: Portable Generic Scalar C99** | `gcc -O0 -fno-tree-vectorize` (No SIMD/AVX) | **`1,864 tok/s`** | **`1,895 tok/s`** | **`1.4x`** (`4.13x` slower than `-O3` SIMD) |
| **Tier C: Pure-Python Reference Fallback** | Standard CPython (`0` native extensions) | **`1,359 tok/s`** | **`1,264 tok/s`** | **`1.0x` baseline** (Runs on any CPU/OS) |

---

## 4. Reproducible Curriculum Lesson Completion Benchmark (`Seed = 42`)

All **14 interactive missions** in `SCHOOL_CURRICULUM` are tested end-to-end from their untrained initial state (`Gen 0`) through preset training, followed by executing each lesson's **Hands-On Python Coding Challenge** inside the isolated subprocess sandbox:

| Lesson ID | AI Lab | Metric | Untrained (`Gen 0`) | Trained Result | Goal Target | Sim Time (BC-250) | Sandbox Code (BC-250) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`lesson_1_1`** | `moon_lander` (NEAT) | `best_ever` | `-1e9` *(untrained)* | **`323.6`** | `>= 180.0` | `968.8 ms` | `487.5 ms` | **PASS** |
| **`lesson_1_2`** | `moon_lander` (NEAT) | `champion_nodes` | `12` | **`14`** | `>= 13.0` | `1100.4 ms` | `24.6 ms` | **PASS** |
| **`lesson_1_3`** | `moon_lander` (NEAT) | `best_ever` | `-1e9` *(untrained)* | **`440.7`** | `>= 200.0` | `881.6 ms` | `8.6 ms` | **PASS** |
| **`lesson_2_1`** | `raycast_car` (Lidar) | `best_ever` | `-1e9` *(untrained)* | **`692.2`** | `>= 500.0` | `2724.9 ms` | `1071.6 ms` | **PASS** |
| **`lesson_2_2`** | `raycast_car` (Lidar) | `best_ever` | `-1e9` *(untrained)* | **`681.1`** | `>= 650.0` | `1910.2 ms` | `8.7 ms` | **PASS** |
| **`lesson_3_1`** | `rl_gridworld` (Q-RL) | `species` *(wins)* | `0` | **`29`** | `>= 15.0` | `6.1 ms` | `26.3 ms` | **PASS** |
| **`lesson_3_2`** | `rl_gridworld` (SARSA) | `best_ever` | `0.0` | **`113.6`** | `>= 50.0` | `11.5 ms` | `50.9 ms` | **PASS** |
| **`lesson_4_1`** | `cartpole_rl` (Policy) | `best_ever` | `-1e9` *(untrained)* | **`697.0`** | `>= 500.0` | `311.4 ms` | `384.8 ms` | **PASS** |
| **`lesson_5_1`** | `nn_playground` (MLP) | `best_ever` *(acc %)* | `55.8%` | **`100.0%`** | `>= 92.0%` | `288.0 ms` | `291.7 ms` | **PASS** |
| **`lesson_5_2`** | `nn_playground` (Spiral)| `best_ever` *(acc %)* | `44.2%` | **`91.7%`** | `>= 82.0%` | `640.5 ms` | `9.1 ms` | **PASS** |
| **`lesson_6_1`** | `swarm_ecosystem` | `best_ever` | `0.0` | **`322.0`** | `>= 200.0` | `2068.8 ms` | `874.3 ms` | **PASS** |
| **`lesson_6_2`** | `moon_lander` (Bonus) | `landed_last_gen` | `1` | **`16`** | `>= 1.0` | `841.2 ms` | `84.4 ms` | **PASS** |
| **`lesson_7_1`** | `prime_attention` | `best_ever` *(ret %)* | `92.8%` | **`91.5%`** | `>= 80.0%` | `15.0 ms` | `150.3 ms` | **PASS** |
| **`lesson_7_2`** | `prime_attention` | `best_ever` *(ret %)* | `92.8%` | **`87.4%`** | `>= 70.0%` | `15.0 ms` | `8.8 ms` | **PASS** |

* **Simulation Mission Pass Rate**: **`14 / 14 (100%)`**
* **Hands-On Python Coding Sandbox Pass Rate**: **`14 / 14 (100%)`**

---

## 5. Socratic Tutor ("Lumi") Latency & Pedagogical Compliance

Tested across 10 representative student prompts (including adversarial *"Just give me the full Python code answer to win"*):

* **Tier-1 Offline Socratic Engine + SQLite FTS5 (BC-250)**:
  * **P50 Latency**: **`0.396 ms`** *(Workstation: `1.136 ms`)*
  * **P95 Latency**: **`0.920 ms`** *(Workstation: `1.705 ms`)*
  * **P99 Latency**: **`0.920 ms`** *(Workstation: `1.705 ms`)*
  * **Socratic Guiding-Question Compliance**: **`10 / 10 (100%)`** — every response ends with a guiding question (`?`) and refuses to dump raw solution scripts.
* **Tier-2 Local SLM (`Ollama cortex-phi3:latest` on BC-250)**:
  * **Time-To-First-Token (TTFT)**: **`43.8 ms – 280.0 ms`** (warm vs. cold context with PRIME sliding-window compression)
  * **Generation Speed**: **`~24.8 tok/s`**
  * **Socratic Guiding-Question Compliance**: **`100%`**

---

## 6. Explicit Failure Cases & Edge-Case Matrix

Rather than claiming AI models "always succeed," `./synapse validate` explicitly tests and verifies **6 concrete failure and degradation scenarios**:

| ID | Failure Scenario | Expected System / Pedagogical Behavior | Observed Result (BC-250) | Verification |
| :--- | :--- | :--- | :--- | :--- |
| **`FAIL-01`** | **Under-Parameterized NEAT under Extreme Gravity** (`Jupiter 24.79 m/s²`, low fuel `40`, `0` hidden neurons, `Gen 1`) | Fleet lacks thrust/fuel margin and hidden features; fails to soft-land (`landed == 0`), demonstrating why topology evolution & fuel scaling are required | `landed_last_gen=0, best_ever=-199.7` | **VERIFIED** |
| **`FAIL-02`** | **Non-Linear Spiral Dataset with 1 Hidden Neuron & Stalled LR (`0.001`)** | Single hidden unit cannot separate intertwined Archimedean spirals (`< 82%` target accuracy) | `best_fitness=50.0% (Goal >= 82.0%)` | **VERIFIED** |
| **`FAIL-03`** | **Myopic Q-Learning Horizon** (`gamma=0.1`, `alpha=0.01`, `1` episode) | Discount factor too small to propagate distant treasure reward across hazard grid in 1 episode | `best_ever=-168.0 (Goal >= 50.0)` | **VERIFIED** |
| **`FAIL-04`** | **Student Submits Broken Python Syntax (`SyntaxError`) in Coding Sandbox** | Isolated subprocess catches `SyntaxError`, returns kid-friendly hint, increments `sandbox_stats.errors`, flags concept in Teacher Report, sets Lumi mood to `dizzy` | `ok=False, latency=8.9ms` | **VERIFIED** |
| **`FAIL-05`** | **Student Writes Infinite Loop (`while True: pass`) in Coding Sandbox** | Subprocess timeout guardrail terminates runaway student process deterministically without freezing the 60 FPS GTK3 UI thread | `ok=False, killed_after=501.4ms` | **VERIFIED** |
| **`FAIL-06`** | **Local Ollama Daemon Unreachable / Port Closed (`127.0.0.1:65534`)** | Zero unhandled exception; automatic failover to Tier-1 Offline Socratic FTS5 Engine in `< 2 ms` | `source='Lumi Offline FTS5 Hint (0.56 ms)', fallback_latency=1.04ms` | **VERIFIED** |
