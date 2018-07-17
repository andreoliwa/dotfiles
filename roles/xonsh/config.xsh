# Disable autocorrect
DISABLE_CORRECTION="true"
unsetopt correct
unsetopt correct_all

# ==> Caveats
# Add the following to your zshrc to access the online help:
if [[ $OSTYPE == darwin* ]]; then
    unalias run-help
    autoload run-help
    HELPDIR=/usr/local/share/zsh/help
fi

test -e "${HOME}/.iterm2_shell_integration.zsh" && source-bash "${HOME}/.iterm2_shell_integration.zsh"
