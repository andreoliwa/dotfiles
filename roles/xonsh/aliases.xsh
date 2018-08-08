# Pipe my public key to my clipboard.
aliases['pubkey'] = "more ~/.ssh/id_rsa.pub | pbcopy | echo '=> Public key copied to pasteboard.'"

# Syntax-highlighted cat (requires python-pygments)
aliases['dog'] = "pygmentize -g"

aliases['cl'] = "clear"
aliases['c'] = "clear"
aliases['pg'] = 'ps -ef | grep'
aliases['lj'] = 'jobs'
aliases['dil'] = 'doitlive'
aliases['dilp'] = 'doitlive play'
aliases['l'] = 'ls -1a'
aliases['la'] = 'ls -la'
aliases['ll'] = 'ls -ll'

aliases['vi'] = "vim"
aliases['v'] = "vim"
# resize images
aliases['resize'] = "mogrify -resize"

aliases['ducks'] = 'du -chs * | sort -rg | head'
