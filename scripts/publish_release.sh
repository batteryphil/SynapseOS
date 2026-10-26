#!/usr/bin/env bash
# ==============================================================================
# SynapseOS Release & Model Publishing Helper
# ==============================================================================
# Prepares and publishes:
#   1. Source repository (Git / GitHub) - < 2 MB total
#   2. Fine-tuned 'cortex-phi3:latest' (2.2 GB) -> Ollama Registry & Hugging Face
#   3. Bootable 'SynapseOS-Debian12-Potato-x86_64.iso' (2.5 GB) ->
#        - Hugging Face Hub (1-click single 2.5 GB ISO download, up to 50 GB/file free)
#        - GitHub Releases (split into 2x <=1.9 GB parts to bypass GitHub's 2.0 GB/file cap)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ISO_PATH="${PROJECT_ROOT}/output/SynapseOS-Debian12-Potato-x86_64.iso"
SHA_PATH="${PROJECT_ROOT}/output/SynapseOS-Debian12-Potato-x86_64.iso.sha256"

usage() {
    cat <<EOF
Usage: ./scripts/publish_release.sh [COMMAND] [ARGS]

Commands:
  --split-for-github      Split the 2.5 GB ISO into two <=1.9 GB parts (.part-aa, .part-ab)
                          so it fits inside GitHub Releases' 2.0 GB per-file limit.
  --push-ollama <USER>    Tag and push 'cortex-phi3:latest' to https://ollama.com/<USER>/cortex-phi3
  --push-hf <USER/REPO>   Upload the full 2.5 GB ISO + SHA256 (single file, 1-click download)
                          to Hugging Face Hub using 'huggingface-cli'.
  --status                Show repository tracked size vs. large release artifacts.
EOF
}

cmd_status() {
    echo "=== SynapseOS Repository & Artifact Summary ==="
    echo "1. Git-Tracked Source + KB + Dataset (fits directly in GitHub repo):"
    du -sh "${PROJECT_ROOT}/cortex" "${PROJECT_ROOT}/workbench" "${PROJECT_ROOT}/distro" "${PROJECT_ROOT}/tests" 2>/dev/null || true
    ls -lh "${PROJECT_ROOT}/cortex/data/cortex_kb.sqlite" "${PROJECT_ROOT}/cortex/forge/cortex_phi3_train.jsonl" "${PROJECT_ROOT}/cortex/forge/Modelfile.phi3"
    echo ""
    echo "2. Large Binary Release Artifacts (ignored by Git, hosted on HF / GitHub Releases / Ollama):"
    if [ -f "${ISO_PATH}" ]; then
        ls -lh "${ISO_PATH}" "${SHA_PATH}"
    else
        echo "   [!] ISO not built yet. Run: sudo ./distro/build-iso.sh --all"
    fi
    if command -v ollama >/dev/null 2>&1; then
        ollama list | grep -E "NAME|cortex-phi3" || true
    fi
}

cmd_split_github() {
    if [ ! -f "${ISO_PATH}" ]; then
        echo "[ERROR] ISO not found at ${ISO_PATH}"
        exit 1
    fi
    echo "[*] Splitting 2.5 GB ISO into <=1.9 GB parts for GitHub Releases (<2.0 GB per-file limit)..."
    split -b 1900M "${ISO_PATH}" "${ISO_PATH}.part-"
    ls -lh "${ISO_PATH}.part-"*
    echo ""
    echo "[✓] Created GitHub Release parts. Users reassemble with:"
    echo "    cat SynapseOS-Debian12-Potato-x86_64.iso.part-* > SynapseOS-Debian12-Potato-x86_64.iso"
    echo "    sha256sum -c SynapseOS-Debian12-Potato-x86_64.iso.sha256"
}

cmd_push_ollama() {
    local user="${1:-}"
    if [ -z "${user}" ]; then
        echo "[ERROR] Specify your Ollama username: ./scripts/publish_release.sh --push-ollama <username>"
        exit 1
    fi
    echo "[*] Tagging cortex-phi3:latest as ${user}/cortex-phi3:latest..."
    ollama cp cortex-phi3:latest "${user}/cortex-phi3:latest"
    echo "[*] Pushing to Ollama Registry (https://ollama.com/${user}/cortex-phi3)..."
    ollama push "${user}/cortex-phi3:latest"
    echo "[✓] Published! Anyone can now run: ollama run ${user}/cortex-phi3"
}

cmd_push_hf() {
    local repo="${1:-}"
    if [ -z "${repo}" ]; then
        echo "[ERROR] Specify Hugging Face repo: ./scripts/publish_release.sh --push-hf <username/SynapseOS>"
        exit 1
    fi
    if ! command -v huggingface-cli >/dev/null 2>&1; then
        echo "[ERROR] huggingface-cli not found. Run inside a venv with huggingface_hub installed."
        exit 1
    fi
    echo "[*] Uploading full 2.5 GB Bootable ISO (single-file 1-click download) to Hugging Face (${repo})..."
    huggingface-cli upload "${repo}" "${ISO_PATH}" SynapseOS-Debian12-Potato-x86_64.iso --repo-type dataset
    huggingface-cli upload "${repo}" "${SHA_PATH}" SynapseOS-Debian12-Potato-x86_64.iso.sha256 --repo-type dataset
    echo "[✓] Uploaded! Direct 1-click ISO download URL:"
    echo "    https://huggingface.co/datasets/${repo}/resolve/main/SynapseOS-Debian12-Potato-x86_64.iso"
}

case "${1:---status}" in
    --split-for-github) cmd_split_github ;;
    --push-ollama)      cmd_push_ollama "${2:-}" ;;
    --push-hf)          cmd_push_hf "${2:-}" ;;
    --status)           cmd_status ;;
    *)                  usage ;;
esac
