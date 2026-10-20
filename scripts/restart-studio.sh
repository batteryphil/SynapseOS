#!/bin/bash
pkill -9 -f "[p]ython3 /usr/local/bin/synapse-studio" 2>/dev/null || true
sleep 0.3
su - synapse -c "DISPLAY=:0 setsid /usr/local/bin/synapse-studio >/tmp/studio.log 2>&1 </dev/null &"
sleep 1.2
ps aux | grep "[s]ynapse-studio"
