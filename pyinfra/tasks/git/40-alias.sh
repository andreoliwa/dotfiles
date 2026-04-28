#!/usr/bin/env bash
# keep-sorted start
alias gl="git pull"
alias gs='git status'
alias gsta="git add -A && git stash push"
alias gstp='git stash pop'
# -u forces listing of all untracked files, overriding repos (e.g. Pedregal) that set
# status.showUntrackedFiles=no for performance; otherwise stray files stay hidden.
alias gsu='git status -u'
alias gwl='git worktree list'
# keep-sorted end
