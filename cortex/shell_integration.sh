#!/usr/bin/env bash
# ==============================================================================
# SynapseOS Cortex Terminal Hook
# Enables instant natural-language Linux and AI assistance directly in bash/zsh.
# ==============================================================================

# Fast command helper shortcut: ?? <question>
??() {
    if [ -z "$*" ]; then
        cortex --help
    else
        cortex cmd "$*"
    fi
}

# AI mentor shortcut: ?ai <topic>
?ai() {
    if [ -z "$*" ]; then
        cortex ai --help
    else
        cortex ai "$*"
    fi
}

# Export cortex to PATH if installed locally
if [ -d "/home/phil/.gemini/antigravity/scratch/synapse-os/bin" ]; then
    export PATH="/home/phil/.gemini/antigravity/scratch/synapse-os/bin:$PATH"
fi
