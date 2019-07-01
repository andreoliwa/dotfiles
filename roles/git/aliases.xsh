aliases['g'] = "git"
aliases['gf'] = "git flow"

aliases['gaa'] = 'git add --all'
aliases['gb'] = 'git branch'
aliases['gba'] = 'git branch --all --verbose'

def _gcd():
    git checkout develop || git checkout development
aliases['gcd'] = _gcd

aliases['gch'] = 'git-checkout-issue'
aliases['gcm'] = 'git checkout master'
aliases['gco'] = 'git checkout'
aliases['gdm'] = 'git diff master'
aliases['gl'] = "git pull"
aliases['glm'] = 'git log ...master'
aliases['gp'] = "git push"
aliases['gs'] = "git status"
aliases['gst'] = "git status"

def _gsta():
    git add -A && git stash
aliases['gsta'] = _gsta
aliases['gstl'] = 'git stash list'
aliases['gstp'] = 'git stash pop'

def _gwip():
    git add -A && git ls-files --deleted -z | xargs git rm && git commit -m "__wip__"
aliases['gwip'] = _gwip

def _gunwip():
    git log -n 1 | grep -q -c "__wip__" && git reset HEAD~1
aliases['gunwip'] = _gunwip
