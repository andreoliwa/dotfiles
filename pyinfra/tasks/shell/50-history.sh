#!/usr/bin/env bash
# Bash history configuration

# Increase history size
# https://unix.stackexchange.com/questions/20861/
export HISTSIZE=30000
export HISTFILESIZE=1000000

# Append to history file, don't overwrite
# https://askubuntu.com/questions/67283/
shopt -s histappend

# Exclude sensitive commands from history
# https://jrnl.sh/en/stable/privacy-and-security/
export HISTIGNORE="$HISTIGNORE:jrnl*"

# Sync history across terminal sessions
# https://superuser.com/questions/1158739/
export PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND ;} history -a; history -r"
