#!/usr/bin/env bash
[[ $OSTYPE != darwin* ]] && return

# JetBrains Toolbox CLI launchers (idea, pycharm, goland, rustrover, etc.)
export PATH="$PATH:$HOME/Library/Application Support/JetBrains/Toolbox/scripts"
