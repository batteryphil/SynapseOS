"""
Cortex Knowledge Base: Linux Guide & System Administration
Comprehensive reference for common and advanced Linux operations, commands, and diagnostics.
"""

from typing import Dict, List, Any

LINUX_TOPICS: Dict[str, Dict[str, Any]] = {
    "gpu_monitoring": {
        "title": "GPU Monitoring & Diagnostics",
        "description": "Monitor GPU temperature, VRAM usage, compute utilization, and active processes.",
        "commands": [
            {
                "cmd": "watch -n 1 radeontop",
                "hardware": "AMD",
                "desc": "Real-time AMD Radeon GPU utilization and VRAM monitor.",
                "safety": "safe"
            },
            {
                "cmd": "rocm-smi",
                "hardware": "AMD ROCm",
                "desc": "AMD ROCm System Management Interface (temperatures, power, clocks, VRAM).",
                "safety": "safe"
            },
            {
                "cmd": "nvidia-smi",
                "hardware": "NVIDIA",
                "desc": "NVIDIA System Management Interface (GPU load, VRAM, running PID list).",
                "safety": "safe"
            },
            {
                "cmd": "nvtop",
                "hardware": "Universal",
                "desc": "Interactive, htop-like monitor for NVIDIA, AMD, and Intel GPUs.",
                "safety": "safe"
            }
        ]
    },
    "kill_runaway_training": {
        "title": "Kill Runaway AI Training or Background Processes",
        "description": "Safely locate and terminate unresponsive Python or training processes holding VRAM.",
        "commands": [
            {
                "cmd": "pkill -f python",
                "desc": "Terminates all running Python processes under the current user.",
                "safety": "caution",
                "notes": "Will stop any active Jupyter notebook, Python scripts, or model servers."
            },
            {
                "cmd": "fuser -v /dev/nvidia* 2>/dev/null",
                "hardware": "NVIDIA",
                "desc": "Identify process IDs holding NVIDIA VRAM.",
                "safety": "safe"
            },
            {
                "cmd": "fuser -v /dev/kfd /dev/dri/render* 2>/dev/null",
                "hardware": "AMD ROCm",
                "desc": "Identify process IDs holding AMD compute/render nodes.",
                "safety": "safe"
            }
        ]
    },
    "hardware_specs": {
        "title": "Hardware Inspection & PCIe Specs",
        "description": "Detailed view of CPU cores, RAM, PCIe buses, and accelerators.",
        "commands": [
            {
                "cmd": "lspci -nnk | grep -iA3 -E 'vga|3d|display'",
                "desc": "Detect graphics cards and currently loaded kernel driver modules.",
                "safety": "safe"
            },
            {
                "cmd": "lscpu",
                "desc": "Display CPU architecture, cores, threads, clock speeds, and vector extensions (AVX/AMX).",
                "safety": "safe"
            },
            {
                "cmd": "free -h",
                "desc": "Display total, used, and available system RAM and Swap.",
                "safety": "safe"
            }
        ]
    },
    "disk_and_storage": {
        "title": "Storage & Large Model File Management",
        "description": "Find where large Hugging Face checkpoints and datasets are consuming space.",
        "commands": [
            {
                "cmd": "ncdu ~/.cache/huggingface",
                "desc": "Interactive disk usage analyzer inside the Hugging Face model cache.",
                "safety": "safe"
            },
            {
                "cmd": "df -h",
                "desc": "Show filesystem disk usage in human-readable gigabytes.",
                "safety": "safe"
            },
            {
                "cmd": "du -sh ~/.cache/* | sort -hr | head -n 10",
                "desc": "List the top 10 largest cache directories consuming your home storage.",
                "safety": "safe"
            }
        ]
    },
    "python_environment": {
        "title": "Python & Package Management with UV",
        "description": "High-performance Python environment management without breaking system packages.",
        "commands": [
            {
                "cmd": "uv venv ai-env && source ai-env/bin/activate",
                "desc": "Create and activate an ultra-fast isolated virtual environment using uv.",
                "safety": "safe"
            },
            {
                "cmd": "uv pip install torch torchvision torchaudio",
                "desc": "Install PyTorch at blazing speed inside the active virtual environment.",
                "safety": "safe"
            },
            {
                "cmd": "uv pip install neat-python gymnasium pygame",
                "desc": "Install NEAT neuroevolution framework and Gymnasium simulation tools.",
                "safety": "safe"
            }
        ]
    }
}
