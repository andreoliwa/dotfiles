# Pipe my public key to my clipboard.
alias pubkey="more ~/.ssh/id_rsa.pub | pbcopy | echo '=> Public key copied to pasteboard.'"

# Syntax-highlighted cat (requires python-pygments)
alias dog="pygmentize -g"

alias cl="clear"
alias c="clear"
alias pg='ps -ef | grep'
alias pkill!="pkill -9 -f "
alias fkill="fkill -v"
alias lj='jobs'
alias dil='doitlive'
alias dilp='doitlive play'

alias l='ls -1a'
alias la='ls -la'
alias ll='ls -ll'

alias reload!='. ~/.zshrc'
alias vi="vim"
alias v="vim"
# resize images
alias resize="mogrify -resize"

alias timezsh="time zsh -i -c echo"

alias ducks='du -chs * | sort -rg | head'

# Shortcuts to trim spaces on strings
alias ltrim="sed -e 's/^ *//'"
alias rtrim="sed -e 's/ *$//'"
alias trim="sed -e 's/^ *//' -e 's/ *$//'"
