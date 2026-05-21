#!/bin/sh

# set reasonable macOS defaults
# inspired by : https://github.com/mathiasbynens/dotfiles
# more can be found here : https://gist.github.com/brandonb927/3195465

if [ "$(uname -s)" != "Darwin" ]; then
    exit 0
fi

set +e

echo "  - Use AirDrop over every interface. srsly this should be a default."
defaults write com.apple.NetworkBrowser BrowseAllInterfaces 1

echo "  - show the ~/Library folder"
chflags nohidden ~/Library

echo "  - disable smart quotes and smart dashes" \
    " as they're annoying when typing code"
defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false
defaults write NSGlobalDomain NSAutomaticDashSubstitutionEnabled -bool false

echo "  - show path bar"
defaults write com.apple.finder ShowPathbar -bool true

echo "  - Don't use native full-screen (separate Space) for MacVim"
defaults write org.vim.MacVim MMNativeFullScreen 0

echo "  - use F1-F12 as standard function keys (Fn for media keys)"
defaults write NSGlobalDomain com.apple.keyboard.fnState -bool true

# Mission Control ctrl-arrow hotkeys (free up ctrl-left/right/up/down for tmux): writing
# AppleSymbolicHotKeys via defaults does not propagate to System Settings on macOS Tahoe (26.x);
# WindowServer keeps using stale bindings until you uncheck them manually in
# System Settings -> Keyboard -> Keyboard Shortcuts -> Mission Control.
