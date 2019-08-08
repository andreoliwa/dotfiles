alias g="git"
alias gf="git flow"

alias gaa='git add --all'
alias gb='git branch'
alias gba='git branch --all --verbose'

alias gcd="git checkout develop"

alias gch='git-checkout-issue'
alias gcm='git checkout master'
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

alias gwip="git add -A && git ls-files --deleted -z | xargs git rm && git commit -m '__wip__'"

alias gunwip="git log -n 1 | grep -q -c '__wip__' && git reset HEAD~1"
