#!/usr/bin/env bash

# Load environment variables and aliases; some files should exist,
# you will get a warning to remind you to create them
# shellcheck source=/dev/null
source "$HOME"/.config/dotfiles/local.env
# shellcheck source=/dev/null
test -f "$HOME"/.config/dotfiles/openssl.env && \
    source "$HOME"/.config/dotfiles/openssl.env
# shellcheck source=/dev/null
test -f "$HOME"/container-apps/aliases.sh && \
    source "$HOME"/container-apps/aliases.sh
# shellcheck source=/dev/null
test -f "$HOME"/container-apps-private/aliases.sh && \
    source "$HOME"/container-apps-private/aliases.sh

# Created with http://bashrcgenerator.com/
PS1="\[\033[38;5;11m\]\w\[$(tput sgr0)\]\[\033[38;5;15m\]\n\A \\$ \[$(tput sgr0)\]"
export PS1

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

############### BEGIN CREATED BY ANSIBLE - DON'T EDIT MANUALLY ###############
# https://github.com/direnv/direnv
eval "$(direnv hook bash)"

# https://github.com/rupa/z/blob/master/z.sh
if [[ $OSTYPE == linux* ]]; then
    export _Z_NO_PROMPT_COMMAND=1
fi
# shellcheck source=/dev/null
source "$HOME"/.local/share/z.sh

# https://github.com/riobard/bash-powerline
# Super quick start, but it doesn't show an icon for stashed commits
# source "$HOME"/.bash-powerline.sh

# https://github.com/magicmonty/bash-git-prompt
# Quick start, show all details of a git repo
if [ -f "$HOME"/.bash-git-prompt/gitprompt.sh ]; then
    # Show a different prompt when there is an active SSH connection
    test -n "$SSH_CONNECTION" && export GIT_PROMPT_THEME=Evermeet_Ubuntu

    # GIT_PROMPT_ONLY_IN_REPO=1
    # shellcheck source=/dev/null
    source "$HOME"/.bash-git-prompt/gitprompt.sh
fi

# brew info bash-completion2
export BASH_COMPLETION_COMPAT_DIR="/usr/local/etc/bash_completion.d"
[[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && \
    source "/usr/local/etc/profile.d/bash_completion.sh"

# Source all scripts. To regenerate this .sh file, run:
# dotfiles-cache-shell-scripts bash
# shellcheck source=/dev/null
test -f "$HOME"/.cache/dotfiles/cached_script.sh && \
    source "$HOME"/.cache/dotfiles/cached_script.sh
############### END CREATED BY ANSIBLE - DON'T EDIT MANUALLY ###############

# Add my private script toolbox as last on the PATH
test -d "$HOME"/Code/toolbox/bin && export PATH="$PATH:$HOME/Code/toolbox/bin"

# Increase Bash history size
# https://unix.stackexchange.com/questions/20861/is-there-a-way-to-set-the-size-of-the-history-list-in-bash-to-more-than-5000-lin#20925
export HISTSIZE=100000
export HISTFILESIZE=100000

# https://askubuntu.com/questions/67283/is-it-possible-to-make-writing-to-bash-history-immediate/67306#67306
shopt -s histappend
PROMPT_COMMAND="history -a;$PROMPT_COMMAND"

# Switch to a CLI editor
export EDITOR=vim

# https://docs.brew.sh/Shell-Completion
if type brew &>/dev/null; then
    if [[ -r "$(brew --prefix)/etc/profile.d/bash_completion.sh" ]]; then
        # shellcheck source=/dev/null
        source "$(brew --prefix)/etc/profile.d/bash_completion.sh"
    else
        for COMPLETION in "$(brew --prefix)/etc/bash_completion.d/"*; do
            # shellcheck source=/dev/null
            [[ -r "$COMPLETION" ]] && source "$COMPLETION"
        done
    fi
fi

# Taken from 'brew info fzf':
# shellcheck source=/dev/null
[ -f "$HOME"/.fzf.bash ] && source "$HOME"/.fzf.bash
