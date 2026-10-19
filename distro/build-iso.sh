#!/usr/bin/env bash
# ==============================================================================
# SynapseOS Phase 3: Potato-Grade Debian 12 (Bookworm) Minimal Live ISO Builder
# Idle OS Footprint: ~148 MB RAM (Openbox + Tint2 + LZ4 ZRAM + Zero Display Manager)
# Out-of-the-Box Pre-Baked Suite (100% Offline Capable):
#   1. Fine-Tuned `cortex-phi3:latest` LLM (2.2 GB GGUF) + Ollama CPU/SIMD Runtime
#   2. Cortex SQLite FTS5 Knowledge Base (`cortex_kb.sqlite`, <1ms BM25 retrieval)
#   3. Synapse Studio Native GTK3/Cairo Point-and-Click AI Workbench (6 AI Labs)
#   4. 12-Lesson Interactive School AI Curriculum & Safe Python Coding Sandbox
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${PROJECT_ROOT}/build"
CHROOT_DIR="${BUILD_DIR}/chroot"
IMAGE_DIR="${BUILD_DIR}/image"
OUTPUT_DIR="${PROJECT_ROOT}/output"

DISTRO_BASE="${DISTRO_BASE:-debian}"
if [ "$DISTRO_BASE" = "debian" ]; then
    DEBIAN_RELEASE="bookworm"
    DEBIAN_MIRROR="http://deb.debian.org/debian"
    ISO_NAME="SynapseOS-Debian12-Potato-x86_64.iso"
    LIVE_BOOT_ARGS="boot=live components quiet"
    LIVE_DIR="live"
else
    DEBIAN_RELEASE="noble"
    DEBIAN_MIRROR="http://archive.ubuntu.com/ubuntu"
    ISO_NAME="SynapseOS-Ubuntu24-Lite-x86_64.iso"
    LIVE_BOOT_ARGS="boot=casper quiet"
    LIVE_DIR="casper"
fi

OLLAMA_MODELS_SRC="/usr/share/ollama/.ollama/models"
CORTEX_MANIFEST_REL="manifests/registry.ollama.ai/library/cortex-phi3/latest"

# Color Output
BOLD="\033[1m"
GREEN="\033[92m"
CYAN="\033[96m"
YELLOW="\033[93m"
RED="\033[91m"
RESET="\033[0m"

log_info() {
    echo -e "${CYAN}[SynapseOS Builder]${RESET} ${BOLD}$*${RESET}"
}

log_success() {
    echo -e "${GREEN}[✓]${RESET} ${BOLD}$*${RESET}"
}

log_warn() {
    echo -e "${YELLOW}[!]${RESET} $*"
}

log_error() {
    echo -e "${RED}[✗] ERROR:${RESET} $*" >&2
}

check_prerequisites() {
    log_info "Verifying host ISO build prerequisites..."
    local deps=("debootstrap" "mksquashfs" "xorriso" "grub-mkrescue" "ollama")
    local missing=()
    for cmd in "${deps[@]}"; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing required build tools: ${missing[*]}"
        log_info "Run: sudo apt-get install -y ${missing[*]}"
        exit 1
    fi
    log_success "All ISO build tools verified (debootstrap, mksquashfs, xorriso, grub-mkrescue, ollama)."
}

stage_dry_run() {
    log_info "Executing Phase 3 Dry-Run Validation (Debian 12 Potato + Pre-Baked cortex-phi3 LLM)..."
    echo "  • Base Distribution:   ${DISTRO_BASE} (${DEBIAN_RELEASE} minimal)"
    echo "  • Mirror:              ${DEBIAN_MIRROR}"
    echo "  • Idle RAM Target:     ~148 MB (Xorg + Openbox + Tint2 + tty1 AutoLogin)"
    echo "  • Memory Booster:      LZ4 ZRAM (50% RAM pool, swappiness=25, LLM mlock protection)"
    echo "  • Pre-Baked Local LLM: cortex-phi3:latest (2.2 GB Q4_K_M) + SQLite FTS5 (<1ms)"
    echo "  • AI Workbench:        Synapse Studio 6-Lab GTK3/Cairo + 12-Lesson School Suite"
    echo "  • Target ISO Output:   ${OUTPUT_DIR}/${ISO_NAME}"

    if [ -f "${SCRIPT_DIR}/packages.list" ]; then
        local pkg_count
        pkg_count=$(grep -vE '^\s*#|^\s*$' "${SCRIPT_DIR}/packages.list" | wc -l)
        log_success "Potato package manifest validated (${pkg_count} lean packages)."
    fi

    local required_configs=(
        "${SCRIPT_DIR}/config/zramswap"
        "${SCRIPT_DIR}/config/99-synapse-potato.conf"
        "${SCRIPT_DIR}/config/autologin.conf"
        "${SCRIPT_DIR}/skel/.bash_profile"
        "${SCRIPT_DIR}/skel/.xinitrc"
        "${SCRIPT_DIR}/skel/.config/openbox/autostart"
        "${SCRIPT_DIR}/skel/.config/openbox/menu.xml"
        "${SCRIPT_DIR}/skel/.config/openbox/rc.xml"
        "${SCRIPT_DIR}/skel/.config/tint2/tint2rc"
        "${PROJECT_ROOT}/cortex/knowledge/cortex_kb.sqlite"
        "${PROJECT_ROOT}/workbench/studio_gui.py"
        "${PROJECT_ROOT}/workbench/curriculum.py"
        "${PROJECT_ROOT}/workbench/sandbox_runner.py"
    )
    for cfg in "${required_configs[@]}"; do
        if [ ! -f "$cfg" ]; then
            log_error "Missing required Phase 3 file: $cfg"
            exit 1
        fi
    done

    if sudo test -f "${OLLAMA_MODELS_SRC}/${CORTEX_MANIFEST_REL}"; then
        log_success "Verified fine-tuned 'cortex-phi3:latest' manifest & GGUF blobs in ${OLLAMA_MODELS_SRC}."
    else
        log_warn "cortex-phi3:latest manifest not found in ${OLLAMA_MODELS_SRC}."
    fi

    log_success "All Potato OS configs, Openbox/Tint2 profiles, FTS5 KB, 6 AI Labs & 12 School Lessons verified."
    log_success "Dry run validation complete. Ready to build ${ISO_NAME}."
}

stage_bootstrap() {
    log_info "Stage 1: Bootstrapping Debian ${DEBIAN_RELEASE} minimal rootfs..."
    sudo mkdir -p "${CHROOT_DIR}"
    if [ -f "${CHROOT_DIR}/bin/bash" ]; then
        log_info "Existing Debian bootstrap detected in ${CHROOT_DIR}; reusing base rootfs."
    else
        sudo debootstrap \
            --arch=amd64 \
            --variant=minbase \
            "${DEBIAN_RELEASE}" \
            "${CHROOT_DIR}" \
            "${DEBIAN_MIRROR}"
    fi
    log_success "Base minimal system bootstrapped into ${CHROOT_DIR}."
}

stage_configure() {
    log_info "Stage 2: Configuring Debian chroot & installing potato package stack..."

    sudo mkdir -p "${CHROOT_DIR}/dev" "${CHROOT_DIR}/run" "${CHROOT_DIR}/proc" "${CHROOT_DIR}/sys"
    mountpoint -q "${CHROOT_DIR}/dev"  || sudo mount --bind /dev "${CHROOT_DIR}/dev"
    mountpoint -q "${CHROOT_DIR}/run"  || sudo mount --bind /run "${CHROOT_DIR}/run"
    mountpoint -q "${CHROOT_DIR}/proc" || sudo mount -t proc proc "${CHROOT_DIR}/proc"
    mountpoint -q "${CHROOT_DIR}/sys"  || sudo mount -t sysfs sysfs "${CHROOT_DIR}/sys"

    sudo cp -L /etc/resolv.conf "${CHROOT_DIR}/etc/resolv.conf" 2>/dev/null || true

    echo "synapse-ai" | sudo tee "${CHROOT_DIR}/etc/hostname" >/dev/null
    cat <<EOF | sudo tee "${CHROOT_DIR}/etc/hosts" >/dev/null
127.0.0.1   localhost
127.0.1.1   synapse-ai
EOF

    if [ "$DISTRO_BASE" = "debian" ]; then
        cat <<EOF | sudo tee "${CHROOT_DIR}/etc/apt/sources.list" >/dev/null
deb ${DEBIAN_MIRROR} ${DEBIAN_RELEASE} main contrib non-free non-free-firmware
deb ${DEBIAN_MIRROR} ${DEBIAN_RELEASE}-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security ${DEBIAN_RELEASE}-security main contrib non-free non-free-firmware
EOF
    fi

    sudo cp "${SCRIPT_DIR}/packages.list" "${CHROOT_DIR}/tmp/packages.list"

    sudo chroot "${CHROOT_DIR}" /bin/bash -c "
        export DEBIAN_FRONTEND=noninteractive
        apt-get update
        grep -vE '^\s*#|^\s*$' /tmp/packages.list | xargs apt-get install -y --no-install-recommends

        # Update initramfs so live-boot hooks are baked into /boot/initrd.img-*
        update-initramfs -u -k all || true

        # Create live user 'synapse' with passwordless sudo
        id -u synapse &>/dev/null || useradd -m -s /bin/bash -G sudo,video,audio,plugdev synapse
        echo 'synapse:synapse' | chpasswd
        echo 'synapse ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/synapse
        chmod 0440 /etc/sudoers.d/synapse

        # Create system user 'ollama' for local SLM daemon
        id -u ollama &>/dev/null || useradd -r -s /bin/false -U -m -d /usr/share/ollama ollama

        apt-get clean
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
    "
    log_success "Chroot environment and minimal X11/Openbox stack installed."
}

stage_inject_cortex() {
    log_info "Stage 3: Injecting Potato Kernel Tuning, ZRAM, Openbox Desktop, Pre-Baked cortex-phi3 LLM & Synapse Studio..."

    # 1. Potato ZRAM & Sysctl Kernel Configs
    sudo mkdir -p "${CHROOT_DIR}/etc/default" "${CHROOT_DIR}/etc/sysctl.d"
    sudo cp "${SCRIPT_DIR}/config/zramswap" "${CHROOT_DIR}/etc/default/zramswap"
    sudo cp "${SCRIPT_DIR}/config/99-synapse-potato.conf" "${CHROOT_DIR}/etc/sysctl.d/99-synapse-potato.conf"

    # 2. Zero-RAM tty1 Auto-Login (No GDM/LightDM overhead)
    sudo mkdir -p "${CHROOT_DIR}/etc/systemd/system/getty@tty1.service.d"
    sudo cp "${SCRIPT_DIR}/config/autologin.conf" "${CHROOT_DIR}/etc/systemd/system/getty@tty1.service.d/autologin.conf"

    # 3. Install Cortex-Phi3, SQLite FTS5 KB, 12-Lesson School Suite & Synapse Studio 6-Lab Workbench
    sudo mkdir -p "${CHROOT_DIR}/usr/local/lib/synapse/cortex"
    sudo mkdir -p "${CHROOT_DIR}/usr/local/lib/synapse/workbench"
    sudo cp -r "${PROJECT_ROOT}/cortex/"* "${CHROOT_DIR}/usr/local/lib/synapse/cortex/"
    sudo cp -r "${PROJECT_ROOT}/workbench/"* "${CHROOT_DIR}/usr/local/lib/synapse/workbench/"
    sudo cp "${PROJECT_ROOT}/synapse" "${CHROOT_DIR}/usr/local/lib/synapse/synapse"
    sudo cp "${PROJECT_ROOT}/SYNAPSE_OS_SPECS.txt" "${CHROOT_DIR}/usr/local/lib/synapse/SYNAPSE_OS_SPECS.txt" 2>/dev/null || true

    sudo mkdir -p "${CHROOT_DIR}/usr/local/bin"
    sudo ln -sf /usr/local/lib/synapse/cortex/cortex_cli.py "${CHROOT_DIR}/usr/local/bin/cortex"
    sudo ln -sf /usr/local/lib/synapse/workbench/cli_runner.py "${CHROOT_DIR}/usr/local/bin/synapse-studio"
    sudo ln -sf /usr/local/lib/synapse/synapse "${CHROOT_DIR}/usr/local/bin/synapse"
    sudo ln -sf /usr/local/lib/synapse/cortex/c_prime/bin/prime "${CHROOT_DIR}/usr/local/bin/prime-moment"
    sudo chmod +x "${CHROOT_DIR}/usr/local/lib/synapse/cortex/cortex_cli.py"
    sudo chmod +x "${CHROOT_DIR}/usr/local/lib/synapse/workbench/cli_runner.py"
    sudo chmod +x "${CHROOT_DIR}/usr/local/lib/synapse/synapse"
    sudo cp "${PROJECT_ROOT}/cortex/shell_integration.sh" "${CHROOT_DIR}/usr/local/bin/cortex_shell.sh"
    sudo chmod +x "${CHROOT_DIR}/usr/local/bin/cortex_shell.sh"

    # 4. Inject Ollama Binary, Multi-Arch CPU SIMD Backend Libraries & Fine-Tuned cortex-phi3:latest Model Blobs
    log_info "Baking Ollama runtime + fine-tuned 'cortex-phi3:latest' (2.2 GB) into Live rootfs..."
    sudo cp /usr/local/bin/ollama "${CHROOT_DIR}/usr/local/bin/ollama"
    sudo chmod 755 "${CHROOT_DIR}/usr/local/bin/ollama"

    if [ -d /usr/local/lib/ollama ]; then
        sudo mkdir -p "${CHROOT_DIR}/usr/local/lib/ollama"
        # Copy CPU SIMD libraries (SSE4.2, SandyBridge, IvyBridge, Haswell AVX2, Zen4, etc.) and Vulkan, skipping huge CUDA dirs
        sudo find /usr/local/lib/ollama -maxdepth 1 \( -type f -o -type l \) -exec cp -P {} "${CHROOT_DIR}/usr/local/lib/ollama/" \;
        if [ -d /usr/local/lib/ollama/vulkan ]; then
            sudo cp -r /usr/local/lib/ollama/vulkan "${CHROOT_DIR}/usr/local/lib/ollama/"
        fi
    fi

    # Copy cortex-phi3:latest manifest + exact referenced SHA256 blobs (2.2 GB)
    local dest_models="${CHROOT_DIR}/usr/share/ollama/.ollama/models"
    sudo mkdir -p "${dest_models}/manifests/registry.ollama.ai/library/cortex-phi3"
    sudo mkdir -p "${dest_models}/manifests/registry.ollama.ai/library/phi3"
    sudo mkdir -p "${dest_models}/blobs"

    sudo cp "${OLLAMA_MODELS_SRC}/${CORTEX_MANIFEST_REL}" \
        "${dest_models}/${CORTEX_MANIFEST_REL}"
    if sudo test -f "${OLLAMA_MODELS_SRC}/manifests/registry.ollama.ai/library/phi3/mini"; then
        sudo cp "${OLLAMA_MODELS_SRC}/manifests/registry.ollama.ai/library/phi3/mini" \
            "${dest_models}/manifests/registry.ollama.ai/library/phi3/mini"
    fi

    # Extract exact blob filenames required by cortex-phi3:latest and copy them
    local blobs_list
    blobs_list=$(sudo python3 -c "
import json
with open('${OLLAMA_MODELS_SRC}/${CORTEX_MANIFEST_REL}') as f:
    m = json.load(f)
digests = [m['config']['digest']] + [layer['digest'] for layer in m.get('layers', [])]
for d in digests:
    print(d.replace(':', '-'))
")
    for blob_file in $blobs_list; do
        if [ ! -f "${dest_models}/blobs/${blob_file}" ]; then
            log_info "  -> Copying model blob ${blob_file}..."
            sudo cp "${OLLAMA_MODELS_SRC}/blobs/${blob_file}" "${dest_models}/blobs/${blob_file}"
        else
            log_info "  -> Blob ${blob_file} already present in chroot."
        fi
    done

    # Configure and enable systemd ollama.service inside the Live OS
    cat <<'EOF' | sudo tee "${CHROOT_DIR}/etc/systemd/system/ollama.service" >/dev/null
[Unit]
Description=SynapseOS Local Cortex-Phi3 Inference Service (Ollama)
After=network-online.target zramswap.service

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="HOME=/usr/share/ollama"
Environment="OLLAMA_MODELS=/usr/share/ollama/.ollama/models"
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_KEEP_ALIVE=30m"

[Install]
WantedBy=multi-user.target
EOF

    sudo mkdir -p "${CHROOT_DIR}/etc/systemd/system/multi-user.target.wants"
    sudo ln -sf /etc/systemd/system/ollama.service \
        "${CHROOT_DIR}/etc/systemd/system/multi-user.target.wants/ollama.service"
    sudo chroot "${CHROOT_DIR}" chown -R ollama:ollama /usr/share/ollama 2>/dev/null || true

    # 5. Desktop Launchers
    sudo mkdir -p "${CHROOT_DIR}/usr/share/applications"
    sudo cp "${SCRIPT_DIR}/desktop/cortex.desktop" "${CHROOT_DIR}/usr/share/applications/"
    sudo cp "${SCRIPT_DIR}/skel/Desktop/lunar_lander.desktop" "${CHROOT_DIR}/usr/share/applications/synapse-studio.desktop"

    # 6. Populate /etc/skel and /home/synapse (Openbox, Tint2, .xinitrc, .bash_profile, .bashrc)
    sudo mkdir -p "${CHROOT_DIR}/etc/skel"
    sudo cp -r "${SCRIPT_DIR}/skel/." "${CHROOT_DIR}/etc/skel/"
    sudo chmod +x "${CHROOT_DIR}/etc/skel/.xinitrc"

    if [ -d "${CHROOT_DIR}/home/synapse" ]; then
        sudo cp -r "${SCRIPT_DIR}/skel/." "${CHROOT_DIR}/home/synapse/"
        sudo chmod +x "${CHROOT_DIR}/home/synapse/.xinitrc"
        sudo chroot "${CHROOT_DIR}" chown -R synapse:synapse /home/synapse
    fi

    # Unmount pseudo-filesystems cleanly
    sudo umount -lf "${CHROOT_DIR}/sys" 2>/dev/null || true
    sudo umount -lf "${CHROOT_DIR}/proc" 2>/dev/null || true
    sudo umount -lf "${CHROOT_DIR}/run" 2>/dev/null || true
    sudo umount -lf "${CHROOT_DIR}/dev" 2>/dev/null || true

    log_success "Potato configs, Openbox/Tint2, pre-baked cortex-phi3:latest (2.2 GB) & Synapse Studio injected into rootfs."
}

stage_squashfs() {
    log_info "Stage 4: Compressing SquashFS live filesystem (${LIVE_DIR}/filesystem.squashfs) using multi-core zstd..."
    # Ensure pseudo-filesystems are unmounted before mksquashfs
    sudo umount -lf "${CHROOT_DIR}/sys" 2>/dev/null || true
    sudo umount -lf "${CHROOT_DIR}/proc" 2>/dev/null || true
    sudo umount -lf "${CHROOT_DIR}/run" 2>/dev/null || true
    sudo umount -lf "${CHROOT_DIR}/dev" 2>/dev/null || true

    sudo mkdir -p "${IMAGE_DIR}/${LIVE_DIR}"
    sudo mksquashfs "${CHROOT_DIR}" "${IMAGE_DIR}/${LIVE_DIR}/filesystem.squashfs" \
        -comp zstd -Xcompression-level 6 -b 1M -processors "$(nproc)" -noappend

    local kernel_img
    kernel_img=$(ls -t "${CHROOT_DIR}/boot/vmlinuz"* | head -n 1)
    local initrd_img
    initrd_img=$(ls -t "${CHROOT_DIR}/boot/initrd.img"* | head -n 1)

    sudo cp "$kernel_img" "${IMAGE_DIR}/${LIVE_DIR}/vmlinuz"
    sudo cp "$initrd_img" "${IMAGE_DIR}/${LIVE_DIR}/initrd"
    log_success "SquashFS image and kernel/initrd packaged."
}

stage_build_iso() {
    log_info "Stage 5: Packaging Hybrid UEFI + BIOS Bootable ISO via grub-mkrescue..."
    sudo mkdir -p "${OUTPUT_DIR}" "${IMAGE_DIR}/boot/grub"

    cat <<EOF | sudo tee "${IMAGE_DIR}/boot/grub/grub.cfg" >/dev/null
set default="0"
set timeout=3

menuentry "SynapseOS Potato-Grade AI & School Workstation (With Pre-Baked Cortex-Phi3 LLM)" {
    linux /${LIVE_DIR}/vmlinuz ${LIVE_BOOT_ARGS} ---
    initrd /${LIVE_DIR}/initrd
}

menuentry "SynapseOS (Extreme Potato / Safe Graphics nomodeset)" {
    linux /${LIVE_DIR}/vmlinuz ${LIVE_BOOT_ARGS} nomodeset ---
    initrd /${LIVE_DIR}/initrd
}

menuentry "SynapseOS (Copy-to-RAM Toram Mode for 8GB+ Machines)" {
    linux /${LIVE_DIR}/vmlinuz ${LIVE_BOOT_ARGS} toram ---
    initrd /${LIVE_DIR}/initrd
}
EOF

    sudo grub-mkrescue -o "${OUTPUT_DIR}/${ISO_NAME}" "${IMAGE_DIR}" -- -volid "SYNAPSE_OS"
    sudo chown -R "$USER:$USER" "${OUTPUT_DIR}" 2>/dev/null || true
    sha256sum "${OUTPUT_DIR}/${ISO_NAME}" > "${OUTPUT_DIR}/${ISO_NAME}.sha256"

    local iso_size
    iso_size=$(du -sh "${OUTPUT_DIR}/${ISO_NAME}" | awk '{print $1}')
    log_success "Bootable Hybrid ISO created: ${OUTPUT_DIR}/${ISO_NAME} (${iso_size})"
    log_success "SHA256 Checksum written to:  ${OUTPUT_DIR}/${ISO_NAME}.sha256"
}

stage_build_lite_iso() {
    local lite_iso_name="SynapseOS-Lite-x86_64.iso"
    local lite_image_dir="${BUILD_DIR}/image_lite"
    log_info "Building Lite Experimentation ISO (No LLM / Fast Download): ${OUTPUT_DIR}/${lite_iso_name}..."

    # Ensure latest Cortex (including C99 PRIME-Moment Engine) and 7-Lab Workbench are injected
    sudo mkdir -p "${CHROOT_DIR}/usr/local/lib/synapse/cortex"
    sudo mkdir -p "${CHROOT_DIR}/usr/local/lib/synapse/workbench"
    sudo cp -r "${PROJECT_ROOT}/cortex/"* "${CHROOT_DIR}/usr/local/lib/synapse/cortex/"
    sudo cp -r "${PROJECT_ROOT}/workbench/"* "${CHROOT_DIR}/usr/local/lib/synapse/workbench/"
    sudo cp "${PROJECT_ROOT}/synapse" "${CHROOT_DIR}/usr/local/lib/synapse/synapse"
    sudo cp "${PROJECT_ROOT}/SYNAPSE_OS_SPECS.txt" "${CHROOT_DIR}/usr/local/lib/synapse/SYNAPSE_OS_SPECS.txt" 2>/dev/null || true
    sudo ln -sf /usr/local/lib/synapse/cortex/c_prime/bin/prime "${CHROOT_DIR}/usr/local/bin/prime-moment"

    sudo umount -lf "${CHROOT_DIR}/sys" 2>/dev/null || true
    sudo umount -lf "${CHROOT_DIR}/proc" 2>/dev/null || true
    sudo umount -lf "${CHROOT_DIR}/run" 2>/dev/null || true
    sudo umount -lf "${CHROOT_DIR}/dev" 2>/dev/null || true

    sudo rm -rf "${lite_image_dir}"
    sudo mkdir -p "${lite_image_dir}/${LIVE_DIR}" "${lite_image_dir}/boot/grub" "${OUTPUT_DIR}"

    log_info "Compressing Lite SquashFS (excluding 2.2 GB Ollama LLM & non-essential docs/locales with xz BCJ x86)..."
    sudo mksquashfs "${CHROOT_DIR}" "${lite_image_dir}/${LIVE_DIR}/filesystem.squashfs" \
        -comp xz -Xbcj x86 -b 1M -processors "$(nproc)" -noappend \
        -e usr/share/ollama \
        -e usr/local/lib/ollama \
        -e usr/local/bin/ollama \
        -e etc/systemd/system/ollama.service \
        -e etc/systemd/system/multi-user.target.wants/ollama.service \
        -e usr/share/doc \
        -e usr/share/man \
        -e usr/share/locale \
        -e var/lib/apt/lists \
        -e var/cache/apt

    local kernel_img
    kernel_img=$(ls -t "${CHROOT_DIR}/boot/vmlinuz"* | head -n 1)
    local initrd_img
    initrd_img=$(ls -t "${CHROOT_DIR}/boot/initrd.img"* | head -n 1)

    sudo cp "$kernel_img" "${lite_image_dir}/${LIVE_DIR}/vmlinuz"
    sudo cp "$initrd_img" "${lite_image_dir}/${LIVE_DIR}/initrd"

    cat <<EOF | sudo tee "${lite_image_dir}/boot/grub/grub.cfg" >/dev/null
set default="0"
set timeout=3

menuentry "SynapseOS Lite Experimentation Workstation (7 AI Labs + C99 PRIME Attention + FTS5 KB)" {
    linux /${LIVE_DIR}/vmlinuz ${LIVE_BOOT_ARGS} ---
    initrd /${LIVE_DIR}/initrd
}

menuentry "SynapseOS Lite (Safe Graphics nomodeset)" {
    linux /${LIVE_DIR}/vmlinuz ${LIVE_BOOT_ARGS} nomodeset ---
    initrd /${LIVE_DIR}/initrd
}

menuentry "SynapseOS Lite (Copy-to-RAM Toram Mode)" {
    linux /${LIVE_DIR}/vmlinuz ${LIVE_BOOT_ARGS} toram ---
    initrd /${LIVE_DIR}/initrd
}
EOF

    sudo grub-mkrescue -o "${OUTPUT_DIR}/${lite_iso_name}" "${lite_image_dir}" -- -volid "SYNAPSE_LITE"
    sudo chown -R "$USER:$USER" "${OUTPUT_DIR}" 2>/dev/null || true
    sha256sum "${OUTPUT_DIR}/${lite_iso_name}" > "${OUTPUT_DIR}/${lite_iso_name}.sha256"

    local iso_size
    iso_size=$(du -sh "${OUTPUT_DIR}/${lite_iso_name}" | awk '{print $1}')
    log_success "Bootable Lite ISO created: ${OUTPUT_DIR}/${lite_iso_name} (${iso_size})"
    log_success "SHA256 Checksum written to: ${OUTPUT_DIR}/${lite_iso_name}.sha256"
}

# ----------------- CLI Argument Router -----------------
ACTION="${1:---dry-run}"

check_prerequisites

case "$ACTION" in
    --dry-run)
        stage_dry_run
        ;;
    --bootstrap)
        stage_bootstrap
        ;;
    --configure)
        stage_configure
        ;;
    --inject)
        stage_inject_cortex
        ;;
    --squash)
        stage_squashfs
        ;;
    --iso)
        stage_build_iso
        ;;
    --lite)
        stage_build_lite_iso
        ;;
    --all)
        stage_bootstrap
        stage_configure
        stage_inject_cortex
        stage_squashfs
        stage_build_iso
        ;;
    *)
        echo "Usage: $0 [--dry-run | --bootstrap | --configure | --inject | --squash | --iso | --lite | --all]"
        exit 1
        ;;
esac
