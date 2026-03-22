#!/usr/bin/env bash
# https://github.com/sharkdp/fd
# fd conflicts with /usr/bin/fd on Linux, so we need to alias it
[[ "$OSTYPE" != "darwin"* ]] && alias fd='fdfind'
