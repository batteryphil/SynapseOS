#!/usr/bin/env bash
# ==============================================================================
# SynapseOS Lite ISO Reassembly & Decompression Script
# Recombines the <90 MB Git-compatible zstd chunks in iso/ and verifies SHA256.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ISO_NAME="SynapseOS-Lite-x86_64.iso"

echo "[1/2] Recombining and decompressing ${ISO_NAME}.zst.part-* -> ${ISO_NAME}..."
cat "${ISO_NAME}".zst.part-* | zstd -d -f -o "${ISO_NAME}"

echo "[2/2] Verifying SHA256 checksum..."
sha256sum -c "${ISO_NAME}.sha256"

echo "[OK] Ready to boot: ${SCRIPT_DIR}/${ISO_NAME} ($(du -sh "${ISO_NAME}" | awk '{print $1}'))"
echo "     Test in QEMU:  qemu-system-x86_64 -enable-kvm -m 2048 -smp 2 -cdrom ${SCRIPT_DIR}/${ISO_NAME}"
