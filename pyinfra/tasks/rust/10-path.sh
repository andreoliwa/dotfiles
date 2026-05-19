#!/usr/bin/env bash
# Cargo binaries (rustup, garden, eza, etc.)
test -d "$HOME/.cargo/bin" && export PATH="$HOME/.cargo/bin:$PATH"
