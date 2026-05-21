#!/usr/bin/env bash
# keep-sorted start
alias g="git"
alias gaa='git add --all'
alias gb='git branch'
alias gba='git branch --all --verbose'
alias gch='git-checkout-issue'
alias gcm='git checkout master || git checkout main'
alias gclean="git delete-merged-branches; git delete-squashed-branches"
alias gco='git checkout'
alias gdm='git diff master'
alias gf="git flow"
alias ghc='gh pr checkout'
alias gl="git pull"
alias glm='git log ...master'
alias gmu='gcm; gu'
alias gp="git push"
alias gs='git status'
alias gsta="git add -A && git stash push"
alias gstl='git stash list'
alias gstp='git stash pop'
# -u forces listing of all untracked files, overriding repos (e.g. Pedregal) that set
# status.showUntrackedFiles=no for performance; otherwise stray files stay hidden.
alias gsu='git status -u'
alias gu="invoke git.tidy-up"
alias gwl='git worktree list'
# keep-sorted end

# Multiline aliases must live outside keep-sorted
alias gwip="git add -A && git ls-files --deleted -z |
xargs git rm && git commit -m '__wip__'"
alias gunwip="git log -n 1 | grep -q -c '__wip__' && git reset HEAD~1"
