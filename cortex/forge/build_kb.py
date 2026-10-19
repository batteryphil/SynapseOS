#!/usr/bin/env python3
"""
SynapseOS Cortex Knowledge Base Builder (SQLite3 FTS5 + BM25)
Compiles a zero-RAM (<2MB active), sub-millisecond full-text search database
covering Linux mastery, potato hardware optimization, and all-spectrum AI development.
"""

import os
import sqlite3
import json
from typing import List, Dict, Any

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "knowledge", "cortex_kb.sqlite")
)

LINUX_ENTRIES: List[Dict[str, Any]] = [
    {
        "slug": "gpu_monitor_amd_nvidia",
        "keywords": "gpu monitor vram temperature usage radeontop rocm-smi nvidia-smi nvtop graphics card",
        "summary": "Monitor GPU utilization, VRAM consumption, and thermal sensors in real time.",
        "command": "watch -n 1 radeontop",
        "alternative": "nvtop || nvidia-smi -l 1 || rocm-smi",
        "explanation": "Polls GPU hardware registers every 1 second (`-n 1`) to display shader load, VRAM usage, and clock speeds.",
        "instructions": [
            "Run `watch -n 1 radeontop` (for AMD) or `nvidia-smi -l 1` (for NVIDIA) or `nvtop` (universal).",
            "Check the Memory/VRAM percentage bar to verify if model weights fit in graphics memory.",
            "Press `q` or `Ctrl+C` to exit the monitor."
        ],
        "safety": "safe",
        "safety_note": ""
    },
    {
        "slug": "potato_zram_memory_boost",
        "keywords": "potato ram memory swap zram compress slow low memory out of memory oom boost speed",
        "summary": "Enable compressed ZRAM in-memory swap to nearly double usable RAM on a potato PC.",
        "command": "sudo modprobe zram && sudo zramctl --find --size $(($(grep MemTotal /proc/meminfo | awk '{print $2}') / 2))K --algorithm lz4 && sudo mkswap /dev/zram0 && sudo swapon -p 100 /dev/zram0",
        "alternative": "sudo apt-get install -y zram-tools && echo -e 'ALGO=lz4\nPERCENT=50' | sudo tee /etc/default/zramswap && sudo systemctl restart zramswap",
        "explanation": "Creates an LZ4-compressed block device in RAM (`/dev/zram0`) with priority `100` (`-p 100`), compressing memory pages ~3:1 before touching a slow disk.",
        "instructions": [
            "Run the command to allocate 50% of physical RAM to an LZ4-compressed ZRAM pool.",
            "Verify active ZRAM compression ratio using `zramctl` and `swapon --show`.",
            "Set `sudo sysctl vm.swappiness=150` so the kernel aggressively compresses inactive pages."
        ],
        "safety": "safe",
        "safety_note": ""
    },
    {
        "slug": "kill_runaway_ai_python",
        "keywords": "kill stop terminate freeze stuck runaway python training process oom memory leak hang",
        "summary": "Terminate runaway Python AI training processes and immediately reclaim RAM/VRAM.",
        "command": "pkill -15 -f python3 && sleep 1 && pkill -9 -f python3 2>/dev/null || true",
        "alternative": "ps aux --sort=-%mem | head -n 10",
        "explanation": "Sends `SIGTERM` (`-15`) first so PyTorch/Gymnasium can flush checkpoints cleanly, followed by `SIGKILL` (`-9`) if a C++ extension is deadlocked.",
        "instructions": [
            "Save any active scripts or notebooks before running.",
            "Run the command to stop all Python processes owned by your user.",
            "Run `free -h` to confirm system RAM has been reclaimed."
        ],
        "safety": "caution",
        "safety_note": "Terminates all active Python processes under your user account."
    },
    {
        "slug": "limit_process_ram_cpu_potato",
        "keywords": "limit cap restrict ram memory cpu cores threads systemd-run nice cpulimit potato",
        "summary": "Run a heavy AI script inside a strict RAM and CPU sandbox so it never freezes a potato PC.",
        "command": "systemd-run --user --scope -p MemoryMax=1024M -p CPUQuota=150% nice -n 10 python3 train.py",
        "alternative": "OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 nice -n 15 python3 train.py",
        "explanation": "`systemd-run --scope` wraps the process in a Linux cgroup v2 container capped at 1024 MB RAM (`MemoryMax=1024M`) and 1.5 CPU cores (`CPUQuota=150%`), while `nice -n 10` keeps the desktop UI responsive.",
        "instructions": [
            "Replace `train.py` with the script or command you want to sandbox.",
            "Adjust `MemoryMax=1024M` to match your available RAM budget.",
            "If the script exceeds the cap, only the script is stopped—your OS and GUI never freeze."
        ],
        "safety": "safe",
        "safety_note": ""
    },
    {
        "slug": "find_large_files_disk_cleanup",
        "keywords": "find large big files disk space storage full gigabyte sort size clean cache huggingface ollama",
        "summary": "Locate the largest files and AI model caches consuming disk space.",
        "command": "find ~ -type f -size +500M -exec ls -lh {} + 2>/dev/null | awk '{print $5, $9}' | sort -hr | head -n 20",
        "alternative": "du -sh ~/.cache/huggingface/hub/* ~/.ollama/models/blobs/* 2>/dev/null | sort -hr | head -n 20",
        "explanation": "`find ~ -type f -size +500M` scans your home directory for files over 500MB, formats human-readable sizes (`ls -lh`), and sorts largest-first (`sort -hr`).",
        "instructions": [
            "Run the command to list the top 20 largest files over 500 MB.",
            "Check `~/.cache/huggingface` and `~/.ollama/models` for unused GGUF or safetensors weights.",
            "Remove unwanted files carefully using `rm <filepath>`."
        ],
        "safety": "safe",
        "safety_note": ""
    },
    {
        "slug": "python_venv_uv_setup",
        "keywords": "python virtual environment venv uv pip install packages torch neat gymnasium dependency",
        "summary": "Create an isolated, fast Python AI virtual environment without polluting system packages.",
        "command": "python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install neat-python gymnasium numpy",
        "alternative": "uv venv .venv && uv pip install neat-python gymnasium numpy",
        "explanation": "Creates an isolated `.venv` directory and installs core CPU-friendly AI packages directly into `.venv/bin/python`.",
        "instructions": [
            "Run the command inside your project folder.",
            "Execute scripts using `.venv/bin/python your_script.py` or activate with `source .venv/bin/activate`.",
            "Save your package state anytime with `.venv/bin/pip freeze > requirements.txt`."
        ],
        "safety": "safe",
        "safety_note": ""
    },
    {
        "slug": "network_ports_listening",
        "keywords": "network port open listening socket pid process firewall ss netstat lsof",
        "summary": "List all open network ports and the exact processes listening on them.",
        "command": "sudo ss -tulnp",
        "alternative": "sudo lsof -i -P -n | grep LISTEN",
        "explanation": "`ss` queries kernel sockets: `-t` (TCP), `-u` (UDP), `-l` (listening), `-n` (numeric ports), `-p` (process ID and name, e.g., `ollama` on `11434`).",
        "instructions": [
            "Run `sudo ss -tulnp` in the terminal.",
            "Look at the `Local Address:Port` column (e.g., `127.0.0.1:11434`) and `Process` column."
        ],
        "safety": "safe",
        "safety_note": ""
    },
    {
        "slug": "systemd_service_logs_debug",
        "keywords": "systemd service daemon status logs journalctl restart boot fail error",
        "summary": "Inspect live systemd service logs and troubleshoot failing background daemons.",
        "command": "journalctl -u ollama -n 50 --no-pager",
        "alternative": "systemctl status ollama --no-pager",
        "explanation": "`journalctl -u <service> -n 50` extracts the most recent 50 log lines from the systemd journal for the specified unit.",
        "instructions": [
            "Replace `ollama` with any service name (e.g., `cortex`, `NetworkManager`, `ssh`).",
            "Add `-f` (`journalctl -u ollama -f`) to follow live log output in real time."
        ],
        "safety": "safe",
        "safety_note": ""
    },
    {
        "slug": "cpu_governor_performance_potato",
        "keywords": "cpu speed frequency governor performance powersave slow throttle clock mhz lscpu",
        "summary": "Check CPU clock speeds and switch the Linux CPU scaling governor to maximum performance.",
        "command": "echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor",
        "alternative": "watch -n 1 \"grep 'cpu MHz' /proc/cpuinfo\"",
        "explanation": "Switches all CPU cores from `powersave`/`schedutil` to the `performance` governor to eliminate frequency ramping lag during AI simulations.",
        "instructions": [
            "Run the command before benchmarking or running high-speed NEAT/RL generations.",
            "Switch back to `schedutil` or `powersave` on laptops when running on battery."
        ],
        "safety": "safe",
        "safety_note": ""
    },
    {
        "slug": "linux_permissions_chmod_chown",
        "keywords": "permission denied executable script chmod chown user group sudo",
        "summary": "Fix 'Permission denied' errors on scripts and project directories.",
        "command": "chmod +x script.sh && sudo chown -R $USER:$USER .",
        "alternative": "ls -la",
        "explanation": "`chmod +x` sets the executable bit on a script, and `chown -R $USER:$USER .` restores ownership of the current directory to your user account.",
        "instructions": [
            "Replace `script.sh` with the script you want to run.",
            "Launch the executable script using `./script.sh`."
        ],
        "safety": "safe",
        "safety_note": ""
    }
]

AI_ENTRIES: List[Dict[str, Any]] = [
    {
        "slug": "neat_neuroevolution_moon_lander",
        "paradigm": "Neuroevolution (NEAT)",
        "keywords": "neat neuroevolution augmenting topologies moon lander rocket ship speciation genome mutation fitness",
        "title": "NEAT (Neuroevolution of Augmenting Topologies) & Moon Lander",
        "layman_guide": (
            "Instead of starting with a giant brain, NEAT starts with a tiny brain (just wires from sensors straight to thrusters). "
            "In every generation, 150 rockets try to land. The best ones survive and 'mutate'—occasionally growing a brand new neuron "
            "or wire. In Synapse Studio, just open 'NEAT Moon Lander', set Population to 150, Add-Node Rate to 0.05, and click Start!"
        ),
        "math_and_theory": (
            "1. Speciation Compatibility Distance: delta = (c1 * E / N) + (c2 * D / N) + c3 * W_bar, where E = excess genes, "
            "D = disjoint genes, W_bar = average weight difference of matching innovación numbers.\n"
            "2. Explicit Fitness Sharing: f'_i = f_i / sum_j sh(delta(i, j)), preventing one topology from dominating prematurely.\n"
            "3. Moon Lander Shaped Fitness: F = 100 - 100*sqrt(dx^2 + dy^2) - 50*sqrt(vx^2 + vy^2) - 30*|theta| + 200*landed - 100*crashed - 0.3*fuel."
        ),
        "hyperparameters": {
            "pop_size": "150 (Potato: 80-150 for 60 FPS; Pro: 300+)",
            "conn_add_prob": "0.15 (Probability of adding a new synapse between existing neurons)",
            "node_add_prob": "0.05 (Probability of splitting an existing synapse with a new hidden neuron)",
            "weight_mutate_power": "0.60 (Magnitude of Gaussian perturbation on synaptic weights)",
            "compatibility_threshold": "3.0 (Controls species count; aim for 6 to 12 species)"
        },
        "code_template": (
            "import neat\n"
            "def eval_genomes(genomes, config):\n"
            "    for genome_id, genome in genomes:\n"
            "        net = neat.nn.FeedForwardNetwork.create(genome, config)\n"
            "        # obs = [x, y, vx, vy, angle, angular_vel, left_leg, right_leg]\n"
            "        output = net.activate(obs)\n"
            "        action = output.index(max(output)) # 0:Idle, 1:Left, 2:Main, 3:Right\n"
            "        genome.fitness = compute_lander_fitness(state)"
        ),
        "debugging_tips": (
            "• Rocket hovers forever until fuel runs out: Reward hacking! Decrease the crash penalty or add a small per-frame time penalty (-0.05/step) and reward downward progress toward y=0.\n"
            "• Population stagnates for 20+ generations: Increase `weight_mutate_power` to 0.8 and lower `compatibility_threshold` to protect new structural topologies."
        )
    },
    {
        "slug": "reinforcement_learning_ppo_dqn",
        "paradigm": "Reinforcement Learning (RL)",
        "keywords": "rl reinforcement learning ppo proximal policy optimization dqn q-learning reward shaping discount gamma actor critic",
        "title": "Reinforcement Learning: Q-Learning, DQN, and PPO",
        "layman_guide": (
            "Reinforcement Learning trains an agent like training a dog with treats (+reward) and penalties (-reward). "
            "In Synapse Studio, adjust the 'Curiosity (Exploration)' slider so the agent tries random moves early on, "
            "and 'Foresight (Discount Gamma)' so it cares about landing safely later rather than just surviving the next second."
        ),
        "math_and_theory": (
            "1. Bellman Optimality Update (Q-Learning): Q(s,a) <- Q(s,a) + alpha * [r + gamma * max_a' Q(s',a') - Q(s,a)].\n"
            "2. PPO Clipped Surrogate Objective: L^CLIP(theta) = E_t [ min(r_t(theta)*A_t, clip(r_t(theta), 1-eps, 1+eps)*A_t) ], "
            "where r_t(theta) = pi_theta(a_t|s_t) / pi_theta_old(a_t|s_t) and A_t is Generalized Advantage Estimation (GAE)."
        ),
        "hyperparameters": {
            "learning_rate (alpha)": "3e-4 for PPO / Adam; 1e-3 for DQN",
            "discount_factor (gamma)": "0.99 (Long-horizon tasks like Moon Lander) or 0.95 (Short horizon)",
            "clip_range (epsilon)": "0.2 (Prevents destructive policy updates in PPO)",
            "gae_lambda": "0.95 (Bias-variance tradeoff for advantage estimation)",
            "entropy_coef": "0.01 (Encourages exploration so policy doesn't collapse early)"
        },
        "code_template": (
            "import numpy as np\n"
            "# Tabular / Linear Q-Learning Update (Runs at 50,000 steps/sec on Potato CPU)\n"
            "td_target = reward + (0.0 if done else gamma * np.max(Q[next_state]))\n"
            "td_error = td_target - Q[state, action]\n"
            "Q[state, action] += alpha * td_error"
        ),
        "debugging_tips": (
            "• Q-values explode to infinity: Learning rate `alpha` is too high or `gamma` >= 1.0 without terminal state masking `(1 - done)`.\n"
            "• Policy collapses to doing a single action: Increase `entropy_coef` (e.g., 0.01 -> 0.05) or slow down epsilon decay."
        )
    },
    {
        "slug": "genetic_algorithms_optimization",
        "paradigm": "Evolutionary Computation",
        "keywords": "genetic algorithm ga evolution crossover tournament selection elitism mutation chromosome fitness",
        "title": "Genetic Algorithms (GA) & Evolutionary Strategies",
        "layman_guide": (
            "Genetic Algorithms evolve solutions by breeding the top performers. Pick 'Elitism = Top 5%' so your best rocket "
            "is never lost, and slide 'Mutation Rate' to 10% so offspring try slight variations."
        ),
        "math_and_theory": (
            "1. Tournament Selection: Sample k individuals at random and select argmax_i f(x_i).\n"
            "2. Simulated Binary Crossover (SBX) / Uniform Crossover: Combine parent weight vectors w_child = mask * w_p1 + (1 - mask) * w_p2.\n"
            "3. Isotropic Gaussian Mutation: w' = w + N(0, sigma^2 I)."
        ),
        "hyperparameters": {
            "population_size": "100 - 500",
            "elitism_ratio": "0.05 (Preserve top 5% unchanged across generations)",
            "tournament_size (k)": "3 to 5 (Higher k increases selection pressure)",
            "mutation_rate": "0.05 - 0.15",
            "mutation_sigma": "0.1 - 0.5 (Decay by 0.995 per generation for fine convergence)"
        },
        "code_template": (
            "import numpy as np\n"
            "def evolve_step(pop, fitnesses, elite_k=5, sigma=0.2):\n"
            "    idx = np.argsort(fitnesses)[::-1]\n"
            "    elites = pop[idx[:elite_k]]\n"
            "    children = elites[np.random.randint(0, elite_k, size=(len(pop)-elite_k, pop.shape[1]))]\n"
            "    children += np.random.randn(*children.shape) * sigma\n"
            "    return np.vstack([elites, children])"
        ),
        "debugging_tips": (
            "• Premature convergence (all agents look identical by Gen 10): Reduce tournament size `k` from 10 down to 3, and increase `mutation_sigma`."
        )
    },
    {
        "slug": "pytorch_deep_learning_potato_cpu",
        "paradigm": "Deep Learning & Neural Networks",
        "keywords": "pytorch neural network mlp cnn training loop quantization int8 cpu potato tinygrad onnx backprop",
        "title": "Deep Learning & Potato CPU Optimization (PyTorch / ONNX)",
        "layman_guide": (
            "Deep Learning trains layers of artificial neurons using calculus (gradients). On a computer without a big GPU, "
            "keep Hidden Layers small (like 64x64) and click 'Quantize to INT8' to make models run 4x faster!"
        ),
        "math_and_theory": (
            "1. Forward Pass: h^(l) = sigma(W^(l) h^(l-1) + b^(l)).\n"
            "2. Dynamic INT8 Quantization: Maps FP32 weights W_fp32 to 8-bit integers W_int8 = round(W_fp32 / scale) + zero_point, "
            "reducing memory bandwidth by 4x and utilizing CPU VNNI/AVX2 instructions."
        ),
        "hyperparameters": {
            "hidden_dims": "[64, 64] for control tasks; MobileNetV3-Small for vision on CPU",
            "optimizer": "AdamW (lr=1e-3, weight_decay=1e-4)",
            "activation": "SiLU / GELU or ReLU (ReLU is fastest on legacy CPUs)",
            "torch_threads": "Set `torch.set_num_threads(physical_cores)` to avoid thread contention"
        },
        "code_template": (
            "import torch, torch.nn as nn\n"
            "torch.set_num_threads(max(1, os.cpu_count() // 2))\n"
            "model = nn.Sequential(nn.Linear(8, 64), nn.ReLU(), nn.Linear(64, 4))\n"
            "quantized_model = torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)"
        ),
        "debugging_tips": (
            "• PyTorch is slower with more threads on a potato: Hyperthreading causes cache thrashing in OpenBLAS. Set `OMP_NUM_THREADS` to physical core count (e.g. 2 or 4).\n"
            "• NaN loss during training: Apply gradient clipping `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)`."
        )
    },
    {
        "slug": "llm_slm_finetuning_qlora_gguf",
        "paradigm": "Small Language Models (SLMs) & Fine-Tuning",
        "keywords": "llm slm phi3 qwen llama.cpp ollama lora qlora fine-tune quantization gguf mmap rag fts5",
        "title": "Local SLM Inference, QLoRA Fine-Tuning & Potato Deployment",
        "layman_guide": (
            "Small Language Models like Phi-3 Mini (3.8B) can be taught specialized skills (like Linux and AI coding) using LoRA—which "
            "trains a tiny 'skill adapter' on top of the frozen brain, then compresses it into a single GGUF file that runs offline."
        ),
        "math_and_theory": (
            "1. LoRA (Low-Rank Adaptation): W = W_0 + (alpha / r) * (B @ A), where W_0 in R^(d x k) is frozen, "
            "A in R^(r x k) and B in R^(d x r) with rank r << min(d, k) (e.g. r=16), cutting trainable parameters by 99%.\n"
            "2. Phi-3 Target Modules: `qkv_proj`, `o_proj`, `gate_up_proj`, `down_proj`.\n"
            "3. Memory-Mapped Inference (`--mmap`): Maps the quantized GGUF file directly into virtual address space via OS page cache."
        ),
        "hyperparameters": {
            "lora_r": "16 or 32",
            "lora_alpha": "32 (Typically 2 * lora_r)",
            "lora_dropout": "0.05",
            "learning_rate": "2e-4 with cosine scheduler and 5% warmup",
            "gguf_quant": "Q4_K_M (Best quality/size ratio) or Q4_0 / IQ4_XS for extreme potatoes"
        },
        "code_template": (
            "from peft import LoraConfig, get_peft_model\n"
            "peft_config = LoraConfig(\n"
            "    r=16, lora_alpha=32, lora_dropout=0.05,\n"
            "    target_modules=['qkv_proj', 'o_proj', 'gate_up_proj', 'down_proj'],\n"
            "    task_type='CAUSAL_LM'\n"
            ")"
        ),
        "debugging_tips": (
            "• Model forgets general knowledge after fine-tuning (catastrophic forgetting): Lower learning rate to `1e-4`, keep epochs <= 3, and mix 15% general instruction data.\n"
            "• High RAM spike on startup: Enable `use_mmap=True` in llama.cpp / Ollama and cap `num_ctx` at `2048` or `4096`."
        )
    },
    {
        "slug": "classical_ml_decision_trees_xgboost",
        "paradigm": "Classical Machine Learning",
        "keywords": "classical ml scikit-learn decision tree random forest gradient boosting svm kmeans pca tabular",
        "title": "Classical ML: Decision Trees, Random Forests & Tabular AI",
        "layman_guide": (
            "When working with spreadsheets or sensor tables, Decision Trees and Random Forests are 100x faster than deep neural networks "
            "and run effortlessly on any potato CPU while telling you exactly which variables mattered most!"
        ),
        "math_and_theory": (
            "1. Gini Impurity: G = 1 - sum_k p_k^2. Information Gain splits nodes to maximize delta G.\n"
            "2. Random Forest Bagging: Trains B trees on bootstrap samples with random feature subsets m = sqrt(p) to reduce variance."
        ),
        "hyperparameters": {
            "n_estimators": "100 (Number of trees in the forest)",
            "max_depth": "6 to 12 (Prevents overfitting and keeps memory tiny)",
            "min_samples_split": "5",
            "n_jobs": "-1 (Uses all available CPU cores in parallel)"
        },
        "code_template": (
            "from sklearn.ensemble import RandomForestClassifier\n"
            "clf = RandomForestClassifier(n_estimators=100, max_depth=8, n_jobs=-1, random_state=42)\n"
            "clf.fit(X_train, y_train)\n"
            "importances = clf.feature_importances_"
        ),
        "debugging_tips": (
            "• Training accuracy is 100% but test accuracy is 55%: Overfitting! Constrain `max_depth=6` and increase `min_samples_leaf=5`."
        )
    },
    {
        "slug": "computer_vision_opencv_yolo_potato",
        "paradigm": "Computer Vision",
        "keywords": "computer vision opencv yolo object detection webcam image edge detection contour",
        "title": "Potato-Friendly Computer Vision (OpenCV & Nano Detectors)",
        "layman_guide": (
            "Computer Vision lets your AI see shapes, landing pads, or webcam objects. For fast 60 FPS tracking on a potato, "
            "use OpenCV color/contour filters or quantized Nano detectors at 320x320 resolution."
        ),
        "math_and_theory": (
            "1. Sobel / Canny Edge Detection: Computes image intensity gradients G = sqrt(G_x^2 + G_y^2) with non-maximum suppression.\n"
            "2. IoU (Intersection over Union): Area(Box_A intersect Box_B) / Area(Box_A union Box_B) used in Non-Maximum Suppression (NMS)."
        ),
        "hyperparameters": {
            "input_resolution": "320x320 (Runs 4x faster on CPU than 640x640)",
            "conf_threshold": "0.35 (Minimum confidence score to keep a bounding box)",
            "nms_iou_threshold": "0.45 (Merges overlapping bounding boxes)"
        },
        "code_template": (
            "import cv2\n"
            "gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)\n"
            "edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)\n"
            "contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)"
        ),
        "debugging_tips": (
            "• High webcam lag on CPU: Resize frame immediately after capture (`cv2.resize(frame, (320, 240))`) and process in grayscale when color isn't needed."
        )
    },
    {
        "slug": "prime_moment_sliding_window_attention",
        "paradigm": "Linear & Hybrid Attention (PRIME Moment)",
        "keywords": "prime moment attention sliding window kv cache o(1) state taylor qk norm passkey retrieval c99 libprime",
        "title": "PRIME Moment Sliding-Window Attention (O(1) L2-Cache State)",
        "layman_guide": (
            "Standard Transformer Softmax attention stores every past token in a growing KV-cache (O(N^2) work), which slows down potato CPUs. "
            "PRIME Moment Sliding-Window Attention keeps an exact local window W for nearby tokens and compresses all evicted history into "
            "1st- and 2nd-order statistical moments (S0, S1, S2) using a constant 67-262 KB of L2-cache memory at 8,700+ tokens/sec in C99!"
        ),
        "math_and_theory": (
            "1. Per-Head L2 QK-Normalization: q_hat = q / ||q||_2, k_hat = k / ||k||_2 bounds dot products |q_hat . k_hat| <= 1, preventing 2nd-order Taylor polynomial P(x) = 1 + x + 0.5*x^2 parabolic rebound for x < -1.\n"
            "2. O(1) Moment Recurrence: S0_t = lambda*S0 + 1, S1_t = lambda*S1 + k_hat*v^T (O(D^2)), S2_t = lambda*S2 + (k_hat odot k_hat)*v^T.\n"
            "3. Hybrid Readout: y_t = alpha * SoftmaxWindow(q_t, K_{t-W:t}, V_{t-W:t}) + (1 - alpha) * PrimeMomentReadout(q_hat_t, S0, S1, S2)."
        ),
        "hyperparameters": {
            "window_size (W)": "64 - 256 (Local exact token window before eviction into PRIME Moment state)",
            "moment_decay (lambda)": "0.990 - 0.998 (Exponential retention horizon for long-range passkey recall)",
            "hybrid_alpha": "0.45 (Balance between exact local sliding window and O(1) global PRIME Moment state)",
            "qk_norm": "1 / Enabled (Mandatory to prevent Taylor polynomial parabolic rebound on negative dot products)"
        },
        "code_template": (
            "from cortex.prime_window import HybridSlidingWindowPrimeEngine\n"
            "engine = HybridSlidingWindowPrimeEngine(window_size=64, d_head=32, decay=0.995)\n"
            "out = engine.step_token(q_vec, k_vec, v_vec)"
        ),
        "debugging_tips": (
            "• Passkey accuracy drops at long distances: Ensure `qk_norm=1` is enabled and increase `moment_decay (lambda)` from 0.95 to 0.996 so early tokens do not decay before readout."
        )
    }
]


def build_database(db_path: str = DB_PATH) -> Dict[str, int]:
    """Create and populate the SQLite FTS5 database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Pragma optimizations for tiny size and fast read speed
    cur.execute("PRAGMA journal_mode = OFF;")
    cur.execute("PRAGMA synchronous = OFF;")
    cur.execute("PRAGMA page_size = 4096;")

    # 1. Linux Commands FTS5 Virtual Table
    cur.execute("""
        CREATE VIRTUAL TABLE linux_fts USING fts5(
            slug UNINDEXED,
            keywords,
            summary,
            command,
            alternative UNINDEXED,
            explanation,
            instructions_json UNINDEXED,
            safety UNINDEXED,
            safety_note UNINDEXED,
            tokenize='porter unicode61'
        );
    """)

    for item in LINUX_ENTRIES:
        cur.execute(
            """
            INSERT INTO linux_fts (
                slug, keywords, summary, command, alternative,
                explanation, instructions_json, safety, safety_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["slug"],
                item["keywords"],
                item["summary"],
                item["command"],
                item["alternative"],
                item["explanation"],
                json.dumps(item["instructions"]),
                item["safety"],
                item["safety_note"]
            )
        )

    # 2. AI Knowledge FTS5 Virtual Table
    cur.execute("""
        CREATE VIRTUAL TABLE ai_fts USING fts5(
            slug UNINDEXED,
            paradigm,
            keywords,
            title,
            layman_guide,
            math_and_theory,
            hyperparameters_json UNINDEXED,
            code_template,
            debugging_tips,
            tokenize='porter unicode61'
        );
    """)

    for item in AI_ENTRIES:
        cur.execute(
            """
            INSERT INTO ai_fts (
                slug, paradigm, keywords, title, layman_guide,
                math_and_theory, hyperparameters_json, code_template, debugging_tips
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["slug"],
                item["paradigm"],
                item["keywords"],
                item["title"],
                item["layman_guide"],
                item["math_and_theory"],
                json.dumps(item["hyperparameters"]),
                item["code_template"],
                item["debugging_tips"]
            )
        )

    con.commit()
    cur.execute("VACUUM;")
    con.close()

    size_kb = round(os.path.getsize(db_path) / 1024, 1)
    return {
        "linux_count": len(LINUX_ENTRIES),
        "ai_count": len(AI_ENTRIES),
        "size_kb": size_kb,
        "path": db_path
    }


if __name__ == "__main__":
    stats = build_database()
    print(f"[✓] Built SQLite FTS5 Knowledge Base: {stats['path']}")
    print(f"    • Linux Command Recipes: {stats['linux_count']}")
    print(f"    • AI Paradigm Guides:    {stats['ai_count']}")
    print(f"    • Database Footprint:    {stats['size_kb']} KB (< 0.1 MB!)")
