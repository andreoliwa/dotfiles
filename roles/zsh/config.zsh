# Disable autocorrect
DISABLE_CORRECTION="true"
unsetopt correct
unsetopt correct_all

# ==> Caveats
# Add the following to your zshrc to access the online help:
unalias run-help
autoload run-help
HELPDIR=/usr/local/share/zsh/help

test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"
