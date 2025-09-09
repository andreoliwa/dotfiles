#!/usr/bin/env bash
alias rsync-default="rsync --human-readable --recursive --times --from0 --verbose --compress --progress --modify-window=1 --iconv=UTF-8-MAC,UTF-8"

# https://stackoverflow.com/questions/17998978/removing-colors-from-output
alias decolorize='sed -r "s/\\x1B\\[([0-9]{1,3}(;[0-9]{1,2})?)?[mGK]//g"'

# Copy to clipboard and still display the output
alias clip='tee /tmp/clipboard.txt | pbcopy; cat /tmp/clipboard.txt'
