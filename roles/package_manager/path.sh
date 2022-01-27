#!/usr/bin/env bash

# Add Homebrew to the Linux PATH
if [[ $OSTYPE == linux* ]]; then
    PATH="$PATH:$(brew --prefix)/bin"
    export PATH
fi
