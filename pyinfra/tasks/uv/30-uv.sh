#!/usr/bin/env bash
# uv tool installs land in ~/.local/bin (dotf, pyinfra, ruff, etc.)
test -d "$HOME/.local/bin" && export PATH="$PATH:$HOME/.local/bin"
