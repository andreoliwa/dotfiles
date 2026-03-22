#!/usr/bin/env bash
# Common environment variables (all machines)

# Terminal editor
export EDITOR='vim'

# X11 display (for tools like feh)
export DISPLAY=:0.0

# Color constants and helper functions (from roles/bash/colors.sh)
export COLOR_LIGHT_GREEN='\033[1;32m'
export COLOR_LIGHT_RED='\033[1;31m'
export COLOR_NONE='\033[0m'

echo_error() {
    echo -e "${COLOR_LIGHT_RED}${*}${COLOR_NONE}"
}
export -f echo_error

echo_success() {
    echo -e "${COLOR_LIGHT_GREEN}${*}${COLOR_NONE}"
}
export -f echo_success
