#!/usr/bin/env bash
# fzf key bindings and completion
# https://github.com/junegunn/fzf

# fzf has included git in FZF_COMPLETION_PATH_COMMANDS since v0.54.0, which clobbers
# git's subcommand completion: bash-completion@2 lazy-loads completions on first Tab,
# so when fzf snapshots existing completions at shell startup, git has none registered
# yet - fzf then permanently registers _fzf_path_completion for git instead.
# No upstream bug filed. Workaround: exclude git so lazy-loading works normally.
export FZF_COMPLETION_PATH_COMMANDS="
  awk bat cat code diff diff3
  emacs emacsclient ex file ftp g++ gcc gvim head hg hx java
  javac ld less more mvim nvim patch perl python ruby
  sed sftp sort source tail tee uniq vi view vim wc xdg-open
  basename bunzip2 bzip2 chmod chown curl cp dirname du
  find grep gunzip gzip hg jar
  ln ls mv open rm rsync scp
  svn tar unzip zip"

# shellcheck source=/dev/null
[[ -f ~/.fzf.bash ]] && source ~/.fzf.bash
