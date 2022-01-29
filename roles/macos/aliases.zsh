#!/usr/bin/env zsh
alias cask="brew cask"
alias services="brew services"

function sha256 {
    shasum -a 256 $1 | head -1 | grep -o '^\S\+'
}

# Display a notification with a given message
alias growl="terminal-notifier -message"
# Useful for notifying when a long script finishes
alias yell="terminal-notifier -title WOOOO -message OOOO!!!"

# When you need disk space
alias cleanup!='brew cleanup --force; brew cask cleanup;'

alias sleep!="pmset sleepnow"
