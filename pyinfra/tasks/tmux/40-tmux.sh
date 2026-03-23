#!/usr/bin/env bash
# https://github.com/tmux/tmux
# https://github.com/tmux-python/tmuxp
export TMUXP_CONFIGDIR="$HOME/.config/tmuxp"

alias t="tmux"
alias tls="tmux list-session"
alias tat="tmux attach-session -d -t"
alias mux="tmuxp load -y "
