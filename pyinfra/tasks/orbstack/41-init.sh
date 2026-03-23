#!/usr/bin/env bash
# OrbStack CLI integration (macOS only)
# https://github.com/orbstack/orbstack
[[ $OSTYPE != darwin* ]] && return
# shellcheck source=/dev/null
source ~/.orbstack/shell/init.bash 2>/dev/null || :
