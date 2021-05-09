if [ -f "$HOME/.bashrc" ]; then
    source $HOME/.bashrc
fi

test -e "${HOME}/.iterm2_shell_integration.bash" && source "${HOME}/.iterm2_shell_integration.bash"

# https://docs.brew.sh/Shell-Completion
if type brew &>/dev/null; then
    HOMEBREW_PREFIX="$(brew --prefix)"
    if [[ -r "${HOMEBREW_PREFIX}/etc/profile.d/bash_completion.sh" ]]; then
        source "${HOMEBREW_PREFIX}/etc/profile.d/bash_completion.sh"
    else
        for COMPLETION in "${HOMEBREW_PREFIX}/etc/bash_completion.d/"*; do
            [[ -r "$COMPLETION" ]] && source "$COMPLETION"
        done
    fi
fi

# Where should I install my own local completions?
# https://github.com/scop/bash-completion/blob/master/README.md#faq
if [[ -d "$HOME/.local/share/bash-completion/completions" ]]; then
    for COMPLETION in "$HOME/.local/share/bash-completion/completions/"*; do
        source "$COMPLETION"
    done
fi

# ==================== BEGIN https://github.com/asdf-vm/asdf
# https://asdf-vm.com/#/core-manage-asdf?id=add-to-your-shell
source $HOME/.asdf/asdf.sh
source $HOME/.asdf/completions/asdf.bash
# ==================== END https://github.com/asdf-vm/asdf

# ==================== BEGIN https://github.com/direnv/direnv
# https://github.com/asdf-community/asdf-direnv#setup
eval "$(asdf exec direnv hook bash)"
direnv() { asdf exec direnv "$@"; }
# ==================== END https://github.com/direnv/direnv
