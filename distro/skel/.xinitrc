#!/usr/bin/env bash
# ~/.xinitrc: Starts the bare-bones Openbox window manager + Synapse Studio (<150MB RAM)

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

xset s off -dpms 2>/dev/null || true
xsetroot -cursor_name left_ptr 2>/dev/null || true
xsetroot -solid "#0f1117" 2>/dev/null || true

exec openbox --startup "/bin/sh -c 'tint2 >/dev/null 2>&1 & /usr/local/bin/synapse-studio >/tmp/synapse-studio.log 2>&1 &'"
