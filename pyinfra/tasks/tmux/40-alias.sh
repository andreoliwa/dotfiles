#!/usr/bin/env bash
# https://github.com/tmux/tmux
# https://github.com/tmux-python/tmuxp
export TMUXP_CONFIGDIR="$HOME/.config/tmuxp"

# keep-sorted start
alias mux="tmuxp load -y "
alias t="tmux"
alias tat="tmux attach-session -d -t"
alias tls="tmux list-session"
# keep-sorted end
