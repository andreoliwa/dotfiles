#!/usr/bin/env bash
# keep-sorted start
alias b='bazel'
alias bb='bazel build'
alias bc='bazel clean'
alias bgr='bazel run //:graphs'
alias bm='bazel run //:go -- mod tidy -e && echo "Success - no errors"'
alias br='bazel run'
alias bs='bazel run //:scaffold'
alias bt='bazel test'
alias bz='bazel run //:gazelle'
alias bza='bazel run //:gazelle -- update .'
# Slow
alias bzs='GAZELLE_NO_FAST=1 bazel run //:gazelle -- update'
# keep-sorted end
