# ~/.bash_profile: Executed by bash for login shells in SynapseOS.

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

# Automatically start X11 + Openbox + Synapse Studio on tty1
if [ -z "${DISPLAY:-}" ] && [ "$(tty)" = "/dev/tty1" ] && [ ! -f /tmp/.synapse_x_started ]; then
    touch /tmp/.synapse_x_started
    sudo startx /home/synapse/.xinitrc >/tmp/startx.log 2>&1 || {
        echo "[!] X11 failed to start. Last lines of /tmp/startx.log:"
        tail -n 20 /tmp/startx.log 2>/dev/null || true
    }
fi
