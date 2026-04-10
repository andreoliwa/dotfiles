#!/usr/bin/env sh
# install.sh - install dotf and pyinfra via uv
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/andreoliwa/dotfiles/master/install.sh | sh
#
# Prerequisites: uv must be installed (https://docs.astral.sh/uv/getting-started/installation/)

set -e

echo "==> Installing dotf (and pyinfra) via uv..."
if [ -t 0 ]; then
    # Running locally (stdin is a terminal) - install from the current directory
    uv tool install --editable . --with-executables-from pyinfra
else
    # Running via curl | sh - install from GitHub
    uv tool install "dotf @ git+https://github.com/andreoliwa/dotfiles.git" --with-executables-from pyinfra
fi

echo "==> Done. Run 'dotf --help' to get started."
