#!/usr/bin/env bash
# ~/.xinitrc: Starts the bare-bones Openbox window manager (<15MB RAM)

xset s off -dpms 2>/dev/null || true
xsetroot -cursor_name left_ptr 2>/dev/null || true

exec openbox-session
