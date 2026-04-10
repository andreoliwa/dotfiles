#!/usr/bin/env bash
# macOS-specific environment setup
[[ $OSTYPE != darwin* ]] && return

export VISUAL='code --wait'

# Homebrew must be first - other tools (pyenv) depend on it being in PATH
eval "$(/opt/homebrew/bin/brew shellenv)"

# macOS file descriptor limit
# https://discussions.apple.com/thread/251000125
ulimit -n 1024
