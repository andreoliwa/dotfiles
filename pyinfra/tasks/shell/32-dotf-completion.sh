#!/usr/bin/env bash
# Generate Bash completion from the current dotf command and inventory.
command -v dotf >/dev/null && eval "$(_DOTF_COMPLETE=source_bash dotf)"
