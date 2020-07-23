#!/usr/bin/env bash
# howdoi bash colors
# Black        0;30     Dark Gray     1;30
# Red          0;31     Light Red     1;31
# Green        0;32     Light Green   1;32
# Brown/Orange 0;33     Yellow        1;33
# Blue         0;34     Light Blue    1;34
# Purple       0;35     Light Purple  1;35
# Cyan         0;36     Light Cyan    1;36
# Light Gray   0;37     White         1;37
export COLOR_LIGHT_GREEN='\033[1;32m'
export COLOR_LIGHT_RED='\033[1;31m'
export COLOR_NONE='\033[0m'

echo_error() {
    echo -e "${COLOR_LIGHT_RED}${*}${COLOR_NONE}"
}
export -f echo_error

echo_success() {
    echo -e "${COLOR_LIGHT_GREEN}${*}${COLOR_NONE}"
}
export -f echo_success
