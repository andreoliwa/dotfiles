export PROJECT_HOME="$HOME/Code"

# To avoid locale errors in some Python modules.
export LC_ALL="en_US.UTF-8"
export LANG="en_US.UTF-8"

# Ansible Python tasks need this environment variable
export PYENV_ROOT=~/.pyenv

# pyenv must be found in the PATH, so "init" can work
test -f ~/.pyenv/bin/pyenv && export PATH="$PATH:$HOME/.pyenv/bin"
eval "$(pyenv init - --no-rehash)"

# flake8 was raising this error on requests.get(url):
# objc[93329]: +[__NSPlaceholderDate initialize] may have been in progress in another thread when fork() was called.
# objc[93329]: +[__NSPlaceholderDate initialize] may have been in progress in another thread when fork() was called. We cannot safely call it or ignore it in the fork() child process. Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.
# https://stackoverflow.com/questions/50168647/multiprocessing-causes-python-to-crash-and-gives-an-error-may-have-been-in-progr/52230415#52230415
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# https://github.com/sdispater/poetry#installation
export PATH="$PATH:$HOME/.poetry/bin"

# https://github.com/pipxproject/pipx#install-pipx
export PATH="$HOME/.local/bin:$PATH"
