#!/usr/bin/env sh
# bootstrap.sh - bootstrap a fresh machine: Xcode CLT, Homebrew, uv, dotfiles repo, dotf.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/andreoliwa/dotfiles/master/bootstrap.sh | sh
#
# Steps:
#   1. Xcode Command Line Tools (macOS only)
#   2. Homebrew (macOS or Linux)
#   3. uv
#   4. ~/dotfiles repo (clone if missing)
#   5. dotf + pyinfra (uv tool install)

set -e

DOTFILES_DIR="${DOTFILES_DIR:-$HOME/dotfiles}"
DOTFILES_REMOTE="${DOTFILES_REMOTE:-https://github.com/andreoliwa/dotfiles.git}"

case "$(uname -s)" in
Darwin) OS=mac ;;
Linux) OS=linux ;;
*) OS=other ;;
esac

step() { printf '\n==> %s\n' "$1"; }

if [ "$OS" = mac ]; then
    step "Xcode Command Line Tools"
    if xcode-select -p >/dev/null 2>&1; then
        echo "    already installed."
    else
        xcode-select --install || true
        echo "    Wait for the GUI installer to finish, then rerun this script."
        exit 1
    fi
fi

step "Homebrew"
if command -v brew >/dev/null 2>&1; then
    echo "    already installed at $(command -v brew)."
else
    NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Make brew visible in this shell.
if [ "$OS" = mac ]; then
    [ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"
    [ -x /usr/local/bin/brew ] && eval "$(/usr/local/bin/brew shellenv)"
elif [ "$OS" = linux ]; then
    [ -x /home/linuxbrew/.linuxbrew/bin/brew ] && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi

step "uv"
if command -v uv >/dev/null 2>&1; then
    echo "    already installed at $(command -v uv)."
else
    brew install uv
fi

step "Dotfiles repo at $DOTFILES_DIR"
if [ -d "$DOTFILES_DIR/.git" ]; then
    echo "    already cloned."
else
    git clone "$DOTFILES_REMOTE" "$DOTFILES_DIR"
fi

step "dotf + pyinfra (uv tool install)"
if [ -t 0 ] && [ -f ./pyproject.toml ] && grep -q '^name = "dotf"' pyproject.toml; then
    # Running from inside the dotfiles repo with a TTY: editable install.
    uv tool install --force --editable . --with-executables-from pyinfra
else
    # Pipe-to-sh path: install from the freshly-cloned dotfiles dir.
    uv tool install --force --editable "$DOTFILES_DIR" --with-executables-from pyinfra
fi

cat <<'EOF'

==> Bootstrap complete.

Next steps:
  1. Ensure $HOME/.local/bin is on PATH (uv tool installs here).
  2. Clone any private overlay repo you use (DOTF_EXTRA_TASKS_DIRS).
  3. Run: dotf provision -s <server>
EOF
