$PROJECT_HOME = str(Path($HOME) / 'Code')

# To avoid locale errors in some Python modules.
$LC_ALL = "en_US.UTF-8"
$LANG = "en_US.UTF-8"

# pyenv must be found in the PATH, so "init" can work
test -f ~/.pyenv/bin/pyenv && $PATH.insert(0, p'~/.pyenv/bin')
pyenv init - --no-rehash > ~/.pyenv/cache/init.xsh
source ~/.pyenv/cache/init.xsh

# flake8 was raising this error on requests.get(url):
# objc[93329]: +[__NSPlaceholderDate initialize] may have been in progress in another thread when fork() was called.
# objc[93329]: +[__NSPlaceholderDate initialize] may have been in progress in another thread when fork() was called. We cannot safely call it or ignore it in the fork() child process. Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.
# https://stackoverflow.com/questions/50168647/multiprocessing-causes-python-to-crash-and-gives-an-error-may-have-been-in-progr/52230415#52230415
$OBJC_DISABLE_INITIALIZE_FORK_SAFETY = "YES"

# https://github.com/pipxproject/pipx#install-pipx
$PATH.insert(0, p'~/.local/bin')
