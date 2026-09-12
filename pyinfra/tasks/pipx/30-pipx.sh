#!/usr/bin/env bash
# pipx completions
# A leftover launcher can still be on PATH after its old Python interpreter is removed.
# Test execution, not just lookup, before enabling completion.
if register-python-argcomplete --help >/dev/null 2>&1; then
    eval "$(register-python-argcomplete pipx)"
fi

# This is created by `pipx ensurepath` on ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
