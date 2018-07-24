aliases["cask"] = "brew cask"
aliases["services"] = "brew services"
aliases["ss"] = "open /System/Library/Frameworks/ScreenSaver.framework/Versions/A/Resources/ScreenSaverEngine.app"

def _sha256(args):
  shasum -a 256 @(args[0]) | head -1 | grep -o '^\S\+'
aliases["sha256"] = _sha256

# Display a notification with a given message
aliases["growl"] = "terminal-notifier -message"
# Useful for notifying when a long script finishes
aliases["yell"] = "terminal-notifier -title WOOOO -message OOOO!!!"

# Get OS X Software Updates, and update installed Ruby gems, Homebrew, npm, and their installed packages
def _update():
    sudo softwareupdate -i -a ; brew update ; brew upgrade ; brew cleanup ; npm update npm -g ; npm update -g ; sudo gem update --system ; sudo gem update
aliases["update"] = _update

# When you need disk space
def _cleanup():
    brew cleanup --force ; brew cask cleanup
aliases["cleanup"] = _cleanup
