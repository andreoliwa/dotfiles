#!/usr/bin/env bash
# https://github.com/eza-community/eza
if command -v eza >/dev/null 2>&1; then
    alias ls='eza'
    alias tree='eza --tree'
fi
