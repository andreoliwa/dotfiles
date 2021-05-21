#!/usr/bin/env bash
export PROJECT_HOME="$HOME/Code"

# To avoid locale errors in some Python modules.
export LC_ALL="en_US.UTF-8"
export LANG="en_US.UTF-8"

# Ansible Python tasks need this environment variable
export PYENV_ROOT=~/.pyenv

# Suggestions made by pyenv init:
# WARNING: `pyenv init -` no longer sets PATH.
# Run `pyenv init` to see the necessary changes to make to your configuration.
eval "$(pyenv init --path)"
eval "$(pyenv init - --no-rehash)"

# flake8 was raising this error on requests.get(url):
# objc[93329]: +[__NSPlaceholderDate initialize] may have been in progress in another thread when fork() was called.
# objc[93329]: +[__NSPlaceholderDate initialize] may have been in progress in another thread when fork() was called. We cannot safely call it or ignore it in the fork() child process. Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.
# https://stackoverflow.com/questions/50168647/multiprocessing-causes-python-to-crash-and-gives-an-error-may-have-been-in-progr/52230415#52230415
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# https://github.com/pipxproject/pipx#install-pipx
export PATH="$HOME/.local/bin:/usr/local/sbin:$PATH"

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONBREAKPOINT
export PYTHONBREAKPOINT=ipdb.set_trace

# Echo all commands in all tasks by default (like 'make' does)
# http://docs.pyinvoke.org/en/stable/concepts/configuration.html#basic-rules
export INVOKE_RUN_ECHO=1

# Use a pseudoterminal by default (display colored output)
# http://docs.pyinvoke.org/en/stable/api/runners.html#invoke.runners.Runner.run
export INVOKE_RUN_PTY=1
