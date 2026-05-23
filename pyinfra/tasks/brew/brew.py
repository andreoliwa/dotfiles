"""Homebrew bootstrap + `brew bundle` against Brewfile.common + Brewfile.<variant>.

Idempotent: skips brew install if already present, and `brew bundle` is a no-op
for packages already installed.
"""

from pathlib import Path

from pyinfra.operations import files
from shared import ASKPASS_PATH, brew_bin as _brew_bin, home_path, make_env, shell, sudo_env

from pyinfra import host

_ENV = make_env()

HERE = Path(__file__).parent
COMMON = HERE / "Brewfile.common"
REMOVE = HERE / "Brewfile.remove"
ASKPASS_SRC = HERE / "askpass.sh"
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
_REMOTE_ASKPASS = home_path(ASKPASS_PATH)



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

files.put(
    name="Install SUDO_ASKPASS helper for brew cask postflight",
    src=str(ASKPASS_SRC),
    dest=_REMOTE_ASKPASS,
    mode="700",
)

# Some cask postflights (e.g. kindle-previewer: launchctl bootout) call sudo
# from a non-TTY subprocess. SUDO_ASKPASS lets those `sudo -A` calls succeed
# without hanging on a hidden prompt. Prime the timestamp first so brief
# child sudo calls reuse it instead of triggering the askpass GUI each time.
shell(
    name="brew bundle (install formulae + casks + taps)",
    commands=[f"sudo -A -v && {_brew_bin()} bundle --global --verbose"],
    _env={
        **sudo_env(),
        "HOMEBREW_NO_AUTO_UPDATE": "1",
        "HOMEBREW_BUNDLE_NO_LOCK": "1",
    },
)


# Process Brewfile.remove: uninstall casks/brews listed there if currently
# installed. Idempotent - missing packages produce no error. `--zap` also
# wipes leftover cask data (preferences, caches).
def _parse_remove_entries(path: Path) -> list[tuple[str, str]]:
    """Parse a Brewfile.remove file into [(kind, name), ...].

    kind is "cask" or "brew"; lines starting with `#` and blank lines are skipped.
    """
    import re

    entries: list[tuple[str, str]] = []
    pattern = re.compile(r'^\s*(cask|brew)\s+"([^"]+)"')
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0]
        match = pattern.match(line)
        if match:
            entries.append((match.group(1), match.group(2)))
    return entries


def _uninstall_entries(entries: list[tuple[str, str]], source_label: str) -> None:
    """Schedule uninstall ops for each (kind, name); idempotent."""
    brew_bin = _brew_bin()
    for kind, name in entries:
        flag = "--cask" if kind == "cask" else "--formula"
        # `--zap` only applies to casks (wipes leftover app data); for brews
        # it's mutually exclusive with `--formula` so omit it there.
        zap = "--zap " if kind == "cask" else ""
        # `--force` lets brew uninstall the cask metadata even when the
        # `/Applications/<App>.app` source is missing (already moved/deleted
        # by the user). Without it, `brew uninstall --cask <name>` aborts with
        # "It seems the App source '...app' is not there."
        force = "--force " if kind == "cask" else ""
        shell(
            name=f"[{source_label}] uninstall {kind} {name} if installed",
            commands=[
                f"if {brew_bin} list {flag} {name} >/dev/null 2>&1; then "
                f"  sudo -A -v && {brew_bin} uninstall {force}{zap}{flag} {name}; "
                f"else "
                f"  echo '  {name}: not installed, skipping'; "
                f"fi",
            ],
            _env={**sudo_env()},
        )


# Always-remove list (Brewfile.remove).
if REMOVE.exists():
    _uninstall_entries(_parse_remove_entries(REMOVE), source_label="Brewfile.remove")

# Cross-variant cleanup: a corp Mac (variant=company) should uninstall anything
# from Brewfile.personal that may have been installed by a previous provision,
# and vice versa. Skips entries that are also in Brewfile.common (defensive,
# though common + variant lists should never overlap in practice).
_OTHER_VARIANT = "personal" if _VARIANT == "company" else "company"
_OTHER_VARIANT_FILE = HERE / f"Brewfile.{_OTHER_VARIANT}"
if _OTHER_VARIANT_FILE.exists():
    _common_names = {name for _, name in _parse_remove_entries(COMMON)}
    _other_entries = [
        (kind, name) for kind, name in _parse_remove_entries(_OTHER_VARIANT_FILE) if name not in _common_names
    ]
    _uninstall_entries(_other_entries, source_label=f"Brewfile.{_OTHER_VARIANT}")
