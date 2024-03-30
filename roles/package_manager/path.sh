#!/usr/bin/env bash

# Add Homebrew to the Linux PATH
if [[ $OSTYPE == linux* ]]; then
    PATH="$PATH:$HOMEBREW_PREFIX/bin"
    export PATH
fi
