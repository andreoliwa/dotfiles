#!/usr/bin/env zsh
# Prezto installation
# see https://github.com/sorin-ionescu/prezto

git clone --recursive https://github.com/sorin-ionescu/prezto.git \
    "${ZDOTDIR:-$HOME}/.zprezto"

setopt EXTENDED_GLOB
# TODO: roles/zsh/files/install_prezto.sh:9:1: E040 Syntax error: syntax error near unexpected token `('
# for rcfile in "${ZDOTDIR:-$HOME}"/.zprezto/runcoms/^README.md(.N); do
#     ln -sf "$rcfile" "${ZDOTDIR:-$HOME}/.${rcfile:t}"
# done
