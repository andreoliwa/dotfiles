#!/usr/bin/env bash
# iTerm2 shell integration (macOS only)
[[ $OSTYPE != darwin* ]] && return
# shellcheck source=/dev/null
test -e "${HOME}/.iterm2_shell_integration.bash" && source "${HOME}/.iterm2_shell_integration.bash"
