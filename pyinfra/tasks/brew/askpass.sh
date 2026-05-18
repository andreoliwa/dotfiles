#!/bin/bash
# SUDO_ASKPASS helper for brew bundle.
# Cask postflight (e.g. kindle-previewer launchctl bootout) calls sudo
# from a non-TTY subprocess, so we need an askpass helper.
#
# First run: GUI prompts via osascript, then password is cached to the
# macOS login keychain (service=dotf-sudo, account=$USER).
# Subsequent runs: silent - keychain entry is read directly, no prompt.
set -e

SERVICE="dotf-sudo"

if pw=$(security find-generic-password -a "$USER" -s "$SERVICE" -w 2>/dev/null); then
    printf '%s' "$pw"
    exit 0
fi

pw=$(osascript <<'OSA'
text returned of (display dialog "sudo password (cached to login keychain for future dotf runs):" \
    default answer "" with hidden answer with title "dotf askpass")
OSA
)

# Cache for next time. -U updates if entry already exists.
security add-generic-password -U -a "$USER" -s "$SERVICE" -w "$pw" >/dev/null 2>&1 || true

printf '%s' "$pw"
