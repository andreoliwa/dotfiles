#!/usr/bin/env bash
# Bash completion setup (all machines)
export BASH_COMPLETION_USER_DIR="$HOME/.local/share/bash-completion"

# User completions directory
# https://github.com/scop/bash-completion/blob/master/README.md#faq
if [[ -d "$BASH_COMPLETION_USER_DIR/completions" ]]; then
    for COMPLETION in "$BASH_COMPLETION_USER_DIR/completions/"*; do
        # shellcheck source=/dev/null
        source "$COMPLETION"
    done
fi

# Typer-installed completions
# https://github.com/tiangolo/typer
if [[ -d "$HOME/.bash_completions/" ]]; then
    for COMPLETION in "$HOME/.bash_completions/"*; do
        # shellcheck source=/dev/null
        [[ -r "$COMPLETION" ]] && source "$COMPLETION"
    done
fi
