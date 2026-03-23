#!/usr/bin/env bash
# zoxide (smart cd replacement)
# https://github.com/ajeetdsouza/zoxide
# Guard added for portability (original had no guard)
command -v zoxide >/dev/null && eval "$(zoxide init bash)"
