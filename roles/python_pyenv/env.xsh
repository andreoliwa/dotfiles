$PROJECT_HOME = str(Path($HOME) / 'Code')

# To avoid locale errors in some Python modules.
$LC_ALL = "en_US.UTF-8"
$LANG = "en_US.UTF-8"

# pyenv must be found in the PATH, so "init" can work
test -f ~/.pyenv/bin/pyenv && $PATH.insert(0, p'~/.pyenv/bin')
pyenv init - --no-rehash > ~/.pyenv/cache/init.xsh
source ~/.pyenv/cache/init.xsh
