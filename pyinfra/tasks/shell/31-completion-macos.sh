#!/usr/bin/env bash
# Homebrew bash completions (macOS only)
# Depends on: 01-env-macos.sh (exports HOMEBREW_PREFIX via brew shellenv)
[[ $OSTYPE != darwin* ]] && return

# Safety: if brew is unavailable (bootstrap, broken install), skip gracefully
command -v brew >/dev/null || return

# brew info bash-completion2
export BASH_COMPLETION_COMPAT_DIR="$HOMEBREW_PREFIX/etc/bash_completion.d"
if [[ -r "$HOMEBREW_PREFIX/etc/profile.d/bash_completion.sh" ]]; then
    # shellcheck source=/dev/null
    source "$HOMEBREW_PREFIX/etc/profile.d/bash_completion.sh"
else
    for COMPLETION in "$HOMEBREW_PREFIX/etc/bash_completion.d/"*; do
        # shellcheck source=/dev/null
        [[ -r "$COMPLETION" ]] && source "$COMPLETION"
    done
fi
