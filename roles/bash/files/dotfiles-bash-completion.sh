#!/usr/bin/env bash
# Autocomplete tags for dotfiles-setup
TAGS=$(yq -r '.[].roles[].tags[]' ~/dotfiles/playbook_*.yml | sort -u)
complete -W "$TAGS" dotfiles-setup
