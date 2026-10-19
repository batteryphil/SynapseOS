# ~/.bash_profile: Executed by bash for login shells in SynapseOS.

if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

# Automatically start X11 + Openbox on tty1 with zero display manager RAM overhead
if [ -z "${DISPLAY:-}" ] && [ "$(tty)" = "/dev/tty1" ]; then
    exec startx >/dev/null 2>&1
fi
