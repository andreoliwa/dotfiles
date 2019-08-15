# Add Homebrew to the Linux PATH
if [[ $OSTYPE == linux* ]]; then
    export PATH="$PATH:$(brew --prefix)/bin"
fi
