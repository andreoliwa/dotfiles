"""Homebrew bootstrap + `brew bundle` against Brewfile.common + Brewfile.<variant>.

Idempotent: skips brew install if already present, and `brew bundle` is a no-op
for packages already installed.
"""

from pathlib import Path

from pyinfra.facts.server import Kernel
from pyinfra.operations import files
from shared import home_path, make_env, shell

from pyinfra import host

_ENV = make_env()

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

_REMOTE_COMMON = home_path(".Brewfile.common")
_REMOTE_VARIANT = home_path(".Brewfile.variant")
_REMOTE_FINAL = home_path(".Brewfile")


def _brew_bin() -> str:
    if host.get_fact(Kernel) == "Darwin":
        return "/opt/homebrew/bin/brew"
    return "/home/linuxbrew/.linuxbrew/bin/brew"


shell(
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
    dest=_REMOTE_COMMON,
    mode="644",
)

files.put(
    name=f"Sync Brewfile.{_VARIANT} to ~/.Brewfile.variant",
    src=str(VARIANT_FILE),
    dest=_REMOTE_VARIANT,
    mode="644",
)

shell(
    name="Concatenate ~/.Brewfile from common + variant",
    commands=[f"cat {_REMOTE_COMMON} {_REMOTE_VARIANT} > {_REMOTE_FINAL}"],
    _env=_ENV,
)

shell(
    name="brew bundle (install formulae + casks + taps)",
    commands=[f"{_brew_bin()} bundle --global --verbose"],
    _env={**_ENV, "HOMEBREW_NO_AUTO_UPDATE": "1", "HOMEBREW_BUNDLE_NO_LOCK": "1"},
)
