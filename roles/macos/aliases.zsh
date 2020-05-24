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

# Get OS X Software Updates, and update installed Ruby gems, Homebrew, npm, and their installed packages
alias update!='sudo softwareupdate -i -a; brew update; brew upgrade; \
    brew cleanup; npm update npm -g; npm update -g; sudo gem update --system; \
    sudo gem update'

# When you need disk space
alias cleanup!='brew cleanup --force; brew cask cleanup;'

alias sleep!="pmset sleepnow"

# See `brew info mysql-client` and see https://pypi.org/project/mysqlclient/
if [[ $OSTYPE == darwin* ]]; then
    export PATH="$PATH:/usr/local/opt/mysql-client/bin"
fi
