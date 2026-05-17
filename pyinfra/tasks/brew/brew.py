"""Homebrew bootstrap + `brew bundle` against Brewfile.common + Brewfile.<variant>.

Idempotent: skips brew install if already present, and `brew bundle` is a no-op
for packages already installed.
"""

from pathlib import Path

from pyinfra.facts.server import Kernel
from pyinfra.operations import files, server

from pyinfra import host

HERE = Path(__file__).parent
COMMON = HERE / "Brewfile.common"
# Server picks the variant via host.data["brew_variant"] -> Brewfile.<variant>.
# Default is "company" (work laptop); personal machines opt in explicitly.
_VARIANT = host.data.get("brew_variant", "company")
VARIANT_FILE = HERE / f"Brewfile.{_VARIANT}"
if not COMMON.exists() or not VARIANT_FILE.exists():
    _missing = [str(p) for p in (COMMON, VARIANT_FILE) if not p.exists()]
    _msg = f"Brewfile(s) not found: {_missing}. Check brew_variant on Server."
    raise SystemExit(_msg)

# brew lives in /opt/homebrew on Apple Silicon, /usr/local on Intel Macs,
# /home/linuxbrew/.linuxbrew on Linux. We set PATH explicitly on each op so
# this task does not depend on shell startup having run already.
_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"{_BREW_PATH}:/usr/bin:/bin:/usr/sbin:/sbin"}


def _brew_bin() -> str:
    if host.get_fact(Kernel) == "Darwin":
        return "/opt/homebrew/bin/brew"
    return "/home/linuxbrew/.linuxbrew/bin/brew"


server.shell(
    name="Install Homebrew if missing",
    commands=[
        "if ! command -v brew >/dev/null 2>&1; then "
        'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL '
        'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; '
        "fi",
    ],
    _env=_ENV,
)

files.put(
    name="Sync Brewfile.common to ~/.Brewfile.common",
    src=str(COMMON),
    dest="~/.Brewfile.common",
    mode="644",
)

files.put(
    name=f"Sync Brewfile.{_VARIANT} to ~/.Brewfile.variant",
    src=str(VARIANT_FILE),
    dest="~/.Brewfile.variant",
    mode="644",
)

server.shell(
    name="Concatenate ~/.Brewfile from common + variant",
    commands=["cat $HOME/.Brewfile.common $HOME/.Brewfile.variant > $HOME/.Brewfile"],
    _env=_ENV,
)

server.shell(
    name="brew bundle (install formulae + casks + taps)",
    commands=[f"{_brew_bin()} bundle --global --no-lock"],
    _env=_ENV,
)
