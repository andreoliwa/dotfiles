#!/usr/bin/env bash
source ~/.cargo/env

export RIPGREP_CONFIG_PATH="$HOME/.ripgreprc"

# On a new laptop, don't create the alias until exa is installed by Rust
if [ -n "$(which exa)" ]; then
    alias ls=exa
    alias tree='exa --tree'
fi
