#!/usr/bin/env bash
# Atuin shell history (MUST load last)
# Prefix "99" ensures this loads after all other fragments.
# atuin hooks PROMPT_COMMAND via bash-preexec; it must run after starship
# sets the prompt, otherwise starship overwrites atuin's hooks.

# shellcheck source=/dev/null
[[ -f ~/.bash-preexec.sh ]] && source ~/.bash-preexec.sh

# https://docs.atuin.sh/configuration/key-binding/#disable-up-arrow
# Guard: atuin's init output calls `bind`, which requires an interactive shell.
# $- contains 'i' only in interactive shells; skip in non-interactive contexts
# (e.g. Claude CLI, scripts) to suppress "bind: line editing not enabled".
[[ $- == *i* ]] && command -v atuin >/dev/null && eval "$(atuin init bash --disable-up-arrow)"
