#!/usr/bin/env bash
# shellcheck source=/dev/null
source ~/.cargo/env

export RIPGREP_CONFIG_PATH="$HOME/.ripgreprc"

# On a new laptop, don't create the alias until exa is installed by Rust
if [ -n "$(which eza)" ]; then
    alias ls=eza
    alias tree='eza --tree'
fi
