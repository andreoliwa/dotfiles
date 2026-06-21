#!/usr/bin/env bash
# https://github.com/garden-rs/garden
# keep-sorted start
# Install with verbosity by default, to show the underlying command being executed
alias ga='garden'
alias gai='garden install -vv'
alias gat='garden test -vv'
alias gi='garden ide -vv'
alias ide='garden ide -vv'
# keep-sorted end

# Pull one or more trees; defaults to all trees when called with no arguments
gal() {
    if [[ $# -eq 0 ]]; then
        garden git '*' pull
    else
        for tree in "$@"; do
            garden git "$tree" pull
        done
    fi
}
