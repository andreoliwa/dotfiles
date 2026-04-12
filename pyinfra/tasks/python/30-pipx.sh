#!/usr/bin/env bash
# pipx completions
command -v register-python-argcomplete >/dev/null && eval "$(register-python-argcomplete pipx)"

# This is created by `pipx ensurepath` on ~/.bashrc
export PATH="$PATH:$HOME/.local/bin"
