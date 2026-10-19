# ~/.bashrc: Executed by bash(1) for non-login shells in SynapseOS.

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# History settings
HISTCONTROL=ignoreboth
shopt -s histappend
HISTSIZE=5000
HISTFILESIZE=10000

# Color prompt
PS1='\[\033[01;32m\]synapse\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

# Aliases
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'
alias gpu='watch -n 1 radeontop 2>/dev/null || watch -n 1 nvidia-smi 2>/dev/null || nvtop'
alias pykill='pkill -f python'

# Load SynapseOS Cortex Assistant
if [ -f /usr/local/bin/cortex_shell.sh ]; then
    source /usr/local/bin/cortex_shell.sh
fi

# SynapseOS Interactive Welcome
echo -e "\033[1;96mWelcome to SynapseOS (AI Experimentation Workstation)\033[0m"
echo -e "\033[2mType \033[1;92m?? <question>\033[0m\033[2m for instant Linux commands & instructions\033[0m"
echo -e "\033[2mType \033[1;95m?ai <topic>\033[0m\033[2m for AI experimentation guidance (e.g. \033[0m?ai neat\033[2m)\033[0m\n"
