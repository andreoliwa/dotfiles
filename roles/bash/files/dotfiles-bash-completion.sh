#!/usr/bin/env bash
# Autocomplete tags for dotfiles-setup
TAGS=$(yq -r '.[].roles[].tags[]' ~/dotfiles/playbook_*.yml)
complete -W "$TAGS" dotfiles-setup
