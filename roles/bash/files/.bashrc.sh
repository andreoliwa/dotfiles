#!/usr/bin/env bash

# Load environment variables and aliases; some files should exist,
# you will get a warning to remind you to create them
# shellcheck source=/dev/null
source "$HOME"/.config/dotfiles/local.env
# shellcheck source=/dev/null
test -f "$HOME"/.config/dotfiles/openssl.env && source "$HOME"/.config/dotfiles/openssl.env
# shellcheck source=/dev/null
test -f "$HOME"/container-apps/aliases.sh && \
    source "$HOME"/container-apps/aliases.sh

# Solution to fix the following error messages:
# Those functions are used by https://github.com/magicmonty/bash-git-prompt
# -bash: setLastCommandState: command not found
# -bash: setGitPrompt: command not found
export PROMPT_COMMAND=

# Turn off nvm for now; it slows down the initialization
export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
# [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# ==================== BEGIN https://github.com/magicmonty/bash-git-prompt
# Quick start, show all details of a git repo
if [ -f "$HOME"/.bash-git-prompt/gitprompt.sh ]; then
    # Show a different prompt when there is an active SSH connection
    test -n "$SSH_CONNECTION" && export GIT_PROMPT_THEME=Evermeet_Ubuntu

    # GIT_PROMPT_ONLY_IN_REPO=1
    # shellcheck source=/dev/null
    source "$HOME"/.bash-git-prompt/gitprompt.sh
fi
# ==================== END https://github.com/magicmonty/bash-git-prompt

# ==================== BEGIN https://github.com/junegunn/fzf/wiki/Examples#autojump
[ -f /usr/local/etc/profile.d/autojump.sh ] && . /usr/local/etc/profile.d/autojump.sh
j() {
    if [[ "$#" -ne 0 ]]; then
        cd "$(autojump "$@")" || return
        return
    fi
    cd "$(autojump -s | sort -k1gr | awk '$1 ~ /[0-9]:/ && $2 ~ /^\// { for (i=2; i<=NF; i++) { print $(i) } }' |  fzf --height 40% --reverse --inline-info)" || exit
}

# https://github.com/wting/autojump#known-issues
export PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND ;} history -a"
# ==================== END https://github.com/junegunn/fzf/wiki/Examples#autojump

# ==================== BEGIN Bash completion / dotfiles
# brew info bash-completion2
export BASH_COMPLETION_COMPAT_DIR="/usr/local/etc/bash_completion.d"
[[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && \
    source "/usr/local/etc/profile.d/bash_completion.sh"

# Source all scripts. To regenerate this .sh file, run:
# dotfiles-cache-shell-scripts bash
# shellcheck source=/dev/null
test -f "$HOME"/.cache/dotfiles/cached_script.sh && \
    source "$HOME"/.cache/dotfiles/cached_script.sh
# ==================== END Bash completion / dotfiles

# ==================== BEGIN https://github.com/pipxproject/pipx#install-pipx
# Taken from "pipx completions" command
eval "$(register-python-argcomplete pipx)"
# ==================== END https://github.com/pipxproject/pipx#install-pipx

# Add my private script toolbox as last on the PATH
test -d "$HOME"/Code/toolbox/bin && export PATH="$PATH:$HOME/Code/toolbox/bin"

# Increase Bash history size
# https://unix.stackexchange.com/questions/20861/is-there-a-way-to-set-the-size-of-the-history-list-in-bash-to-more-than-5000-lin#20925
export HISTSIZE=100000
export HISTFILESIZE=100000

# https://askubuntu.com/questions/67283/is-it-possible-to-make-writing-to-bash-history-immediate/67306#67306
shopt -s histappend

# https://jrnl.sh/en/stable/privacy-and-security/
export HISTIGNORE="$HISTIGNORE:jrnl *"

# Switch from a CLI editor to VSCode in wait mode
export EDITOR='code --wait'

# https://github.com/junegunn/fzf
# Taken from 'brew info fzf' (and edited by an ansible role):
# shellcheck source=/dev/null
[ -f ~/.fzf.bash ] && source ~/.fzf.bash

# shellcheck source=/dev/null
test -f "$HOME"/container-apps-private/aliases.sh && \
    source "$HOME"/container-apps-private/aliases.sh

# https://github.com/starship/starship
eval "$(starship init bash)"
