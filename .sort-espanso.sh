#!/usr/bin/env bash
# Sort espanso match files: matches by trigger, keys alphabetically within each match
set -euo pipefail

for file in "$@"; do
    yq -i '.matches |= sort_by(.trigger, .replace) | .matches[] |= (to_entries | sort_by(.key) | from_entries)' "$file"
done
