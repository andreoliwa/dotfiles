#!/usr/bin/env bash
# Autocomplete tags for dotfiles-setup
TAGS=$(yq e '.[].roles[].tags[]' ~/dotfiles/playbook_*.yml | sort -u | tail +2)
complete -W "$TAGS" dotfiles-setup
