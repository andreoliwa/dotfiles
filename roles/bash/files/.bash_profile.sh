#!/usr/bin/env bash

# Suggestions made by pyenv init:
# WARNING: `pyenv init -` no longer sets PATH.
# Run `pyenv init` to see the necessary changes to make to your configuration.
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

# shellcheck disable=SC1091
test -f "$HOME/.bashrc" && source "${HOME}/.bashrc"
# shellcheck disable=SC1091
test -e "${HOME}/.iterm2_shell_integration.bash" && source "${HOME}/.iterm2_shell_integration.bash"

# https://docs.brew.sh/Shell-Completion
if type brew &>/dev/null; then
    HOMEBREW_PREFIX="$(brew --prefix)"
    if [[ -r "${HOMEBREW_PREFIX}/etc/profile.d/bash_completion.sh" ]]; then
        # shellcheck disable=SC1091
        source "${HOMEBREW_PREFIX}/etc/profile.d/bash_completion.sh"
    else
        for COMPLETION in "${HOMEBREW_PREFIX}/etc/bash_completion.d/"*; do
            # shellcheck source=/dev/null
            [[ -r "$COMPLETION" ]] && source "$COMPLETION"
        done
    fi
fi

# Where should I install my own local completions?
# https://github.com/scop/bash-completion/blob/master/README.md#faq
export BASH_COMPLETION_USER_DIR="$HOME/.local/share/bash-completion"
if [[ -d "$BASH_COMPLETION_USER_DIR/completions" ]]; then
    for COMPLETION in "$BASH_COMPLETION_USER_DIR/completions/"*; do
        # shellcheck source=/dev/null
        source "$COMPLETION"
    done
fi

# ssh-agent single sign-on configuration, agent forwarding, the agent protocol.
# https://www.ssh.com/academy/ssh/agent
# This is needed to load other SSH keys apart from the default "id_rsa"
eval "$(ssh-agent -s)" > /dev/null

# ==================== BEGIN https://github.com/asdf-vm/asdf
# https://asdf-vm.com/#/core-manage-asdf?id=add-to-your-shell
# shellcheck disable=SC1091
source "$HOME/.asdf/asdf.sh"
# shellcheck disable=SC1091
source "$HOME/.asdf/completions/asdf.bash"
# ==================== END https://github.com/asdf-vm/asdf

# ==================== BEGIN https://github.com/direnv/direnv
# https://github.com/asdf-community/asdf-direnv#setup
eval "$(asdf exec direnv hook bash)"
direnv() { asdf exec direnv "$@"; }
# ==================== END https://github.com/direnv/direnv
