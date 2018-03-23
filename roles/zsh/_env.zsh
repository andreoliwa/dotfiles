export EDITOR='code'
export VISUAL='code'
# For ped: https://github.com/sloria/ped
export PED_EDITOR='vim'
export TERM=xterm-256color

# Used by karma: Since we use cask to install browsers, the bin files will be located
# in ~/Applications instead of /Applications (Mac-OSX specific)
export CHROME_BIN="$HOME/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
export FIREFOX_BIN="$HOME/Applications/Firefox.app/Contents/MacOS/firefox-bin"

if [[ $OSTYPE == linux* ]]; then
    export BROWSER=chromium-browser

    # https://faq.i3wm.org/question/2498/ssh-sessions-in-i3/
    if [[ "$DESKTOP_SESSION" = "i3" ]]; then
        export $(gnome-keyring-daemon -s)
    fi
fi
