# Pipe my public key to my clipboard.
alias pubkey="more ~/.ssh/id_rsa.pub | pbcopy | echo '=> Public key copied to pasteboard.'"

# Syntax-highlighted cat (requires python-pygments)
alias dog="pygmentize -g"

alias cl="clear"
alias c="clear"
alias pg='ps -ef | grep'
alias lj='jobs'
alias dil='doitlive'
alias dilp='doitlive play'
alias l='ls -1a'
alias la='ls -la'

alias reload!='. ~/.zshrc'
alias vi="vim"
alias v="vim"
# resize images
alias resize="mogrify -resize"

alias grepalias='alias | grep '
alias ducks='du -chs * | sort -rg | head'
