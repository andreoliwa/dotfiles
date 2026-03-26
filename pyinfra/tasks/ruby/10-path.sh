#!/usr/bin/env bash
# Ruby user-installed gems
test -d "$HOME/.gem/ruby/2.6.0/bin" && export PATH="$PATH:$HOME/.gem/ruby/2.6.0/bin"
