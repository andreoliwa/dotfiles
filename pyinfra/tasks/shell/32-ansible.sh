#!/usr/bin/env bash
# TODO Legacy Ansible bridge: source all role shell scripts via cached_script.sh
#  This loads aliases, env, path, and functions from Ansible roles that
#  haven't been migrated to shell.d fragments yet.
#  To regenerate: dotfiles-cache-shell-scripts bash
#  shellcheck source=/dev/null
test -f "$HOME/.cache/dotfiles/cached_script.sh" && source "$HOME/.cache/dotfiles/cached_script.sh"
