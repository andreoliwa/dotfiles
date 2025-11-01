#!/usr/bin/env bash
alias g="git"
alias gf="git flow"

alias gaa='git add --all'
alias gb='git branch'
alias gba='git branch --all --verbose'

alias gcd='git checkout develop || git checkout development'
alias gd='git checkout develop || git checkout development || git checkout master || git checkout main'
alias gm='git checkout master || git checkout main || git checkout develop || git checkout development'

alias gch='git-checkout-issue'
alias gcm='git checkout master || git checkout main'
alias gco='git checkout'
alias gdm='git diff master'
alias gl="git pull"
alias glm='git log ...master'
alias gp="git push"
alias gs="git status"
alias gst="git status"

alias gsta="git add -A && git stash push"
alias gstl='git stash list'
alias gstp='git stash pop'

alias gwip="git add -A && git ls-files --deleted -z |
xargs git rm && git commit -m '__wip__'"

alias gunwip="git log -n 1 | grep -q -c '__wip__' && git reset HEAD~1"

# Manually clean up old draft commits that aren't part of current stack
alias gclean="git branchless hide 'draft() - stack(@)'"

# Git update: pull, sync branches, and auto-cleanup old draft commits from smartlog
alias gu="git pull; git sync; gclean 2>/dev/null || true"
alias gmu='gcm; gu'

alias ghc='gh pr checkout'

# Shortcut to commit files with a message
function co {
    all_args="$*"
    git commit -m "${all_args}"
}
