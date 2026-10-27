#!/usr/bin/env bash
# ~/.xinitrc: Starts the bare-bones Openbox window manager + Synapse Studio (<150MB RAM)

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

xset s off -dpms 2>/dev/null || true
xsetroot -cursor_name left_ptr 2>/dev/null || true
xsetroot -solid "#0f1117" 2>/dev/null || true

# Pre-map cortex-phi3 in background after GUI renders on machines with >=2.4GB RAM
(
    sleep 3
    python3 -c 'import sys; sys.path.insert(0, "/usr/local/lib/synapse"); from cortex.engine import CortexEngine; CortexEngine().preload_model()' >/dev/null 2>&1 || true
) </dev/null >/dev/null 2>&1 &

exec openbox --startup "/bin/sh -c 'tint2 >/dev/null 2>&1 & /usr/local/bin/synapse-studio >/tmp/synapse-studio.log 2>&1 &'"
