#!/usr/bin/env bash
# ==============================================================================
# SynapseOS 1-Command Full LLM ISO Downloader, Verifier & QEMU Launcher
# ==============================================================================
# Downloads the Full 2.5 GB Bootable ISO (including the fine-tuned 2.2 GB
# cortex-phi3:latest LLM, Ollama runtime, C99 PRIME-Moment engine, 7 AI Labs,
# and all 325 K-12 lessons) from GitHub Releases, reassembles the split parts,
# verifies the SHA256 checksum, and optionally boots it in QEMU/KVM.
#
# Usage:
#   ./scripts/download_and_boot_full_iso.sh              # Download, verify & boot in QEMU
#   ./scripts/download_and_boot_full_iso.sh --download   # Download & verify ISO only (for USB / VirtualBox)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_DIR="${PROJECT_ROOT}/output"
ISO_NAME="SynapseOS-Debian12-Potato-x86_64.iso"
ISO_PATH="${OUT_DIR}/${ISO_NAME}"
SHA_PATH="${OUT_DIR}/${ISO_NAME}.sha256"

REPO="batteryphil/SynapseOS"
RELEASE_TAG="${SYNAPSE_RELEASE_TAG:-v1.0-k12}"
BASE_URL="https://github.com/${REPO}/releases/download/${RELEASE_TAG}"

mkdir -p "${OUT_DIR}"
cd "${OUT_DIR}"

if [ -f "${ISO_PATH}" ] && [ -f "${SHA_PATH}" ]; then
    echo "[*] Existing Full ISO found at ${ISO_PATH}. Verifying SHA256..."
    if sha256sum -c "${ISO_NAME}.sha256" >/dev/null 2>&1; then
        echo "[✓] SHA256 verified! Skipping download."
    else
        echo "[!] Checksum mismatch on existing ISO; re-downloading..."
        rm -f "${ISO_PATH}"
    fi
fi

if [ ! -f "${ISO_PATH}" ]; then
    echo "=== Downloading SynapseOS Full LLM Bootable ISO (${RELEASE_TAG}) ==="
    echo "Includes: Debian 12 + Openbox + Fine-Tuned cortex-phi3 LLM (2.2 GB) + C99 PRIME + 325 K-12 Lessons"
    curl -fL --progress-bar -O "${BASE_URL}/${ISO_NAME}.sha256"
    curl -fL --progress-bar -O "${BASE_URL}/${ISO_NAME}.part-aa"
    curl -fL --progress-bar -O "${BASE_URL}/${ISO_NAME}.part-ab"

    echo "[*] Reassembling 2.5 GB ${ISO_NAME} from parts..."
    cat "${ISO_NAME}.part-aa" "${ISO_NAME}.part-ab" > "${ISO_NAME}"
    rm -f "${ISO_NAME}.part-aa" "${ISO_NAME}.part-ab"

    echo "[*] Verifying SHA256 checksum..."
    sha256sum -c "${ISO_NAME}.sha256"
    echo "[✓] Full Bootable ISO ready at: ${ISO_PATH}"
fi

echo ""
echo "======================================================================"
echo "Full ISO Path: ${ISO_PATH} ($(du -sh "${ISO_PATH}" | awk '{print $1}'))"
echo "  • Flash to USB:   sudo dd if=${ISO_PATH} of=/dev/sdX bs=4M status=progress oflag=sync"
echo "  • VirtualBox/VM:  Attach ${ISO_PATH} as Optical Drive (4 GB RAM, 2 Cores)"
echo "======================================================================"

if [ "${1:-}" = "--download" ] || [ "${1:-}" = "--no-boot" ]; then
    exit 0
fi

if command -v qemu-system-x86_64 >/dev/null 2>&1; then
    echo "[*] Launching ${ISO_NAME} in QEMU (4 GB RAM, 2 CPU Cores)..."
    KVM_ARGS=""
    if [ -w /dev/kvm ]; then
        KVM_ARGS="-enable-kvm -cpu host"
    fi
    exec qemu-system-x86_64 ${KVM_ARGS} -m 4096 -smp 2 -cdrom "${ISO_PATH}" -vga virtio -display default,show-cursor=on
else
    echo "[i] Install 'qemu-system-x86' to boot directly, or boot ${ISO_PATH} in VirtualBox / VMware / USB."
fi
