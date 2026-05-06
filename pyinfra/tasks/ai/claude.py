"""Claude Code installs and add-ons.

Convention for overlay-paired tasks: this module exports named functions and
has NO module-level pyinfra ops. Importing it must be side-effect-free so an
external orchestrator (discovered via ``DOTF_EXTRA_TASKS_DIRS``) can call
functions in any order, interleaving its own ops freely.

``discover_tasks()`` in ``lib.py`` prefers files from extra tasks dirs over
this one when stems collide, so when an overlay is present this file is
imported but not included by pyinfra directly.
"""

from pathlib import Path

from pyinfra.facts.server import Home
from pyinfra.operations import brew, git, server

from pyinfra import host

CCNOTIFY_REPO = "https://github.com/dazuiba/CCNotify.git"
CCNOTIFY_CLONE_DIR = "dev/CCNotify"
CCNOTIFY_INSTALL_DIR = ".claude/ccnotify"

CAVEMAN_MARKETPLACE = "JuliusBrussee/caveman"
CAVEMAN_PLUGIN = "caveman@caveman"


def _home() -> Path:
    return Path(host.get_fact(Home))


def clone_ccnotify() -> None:
    """Clone dazuiba/CCNotify into ~/dev/CCNotify (idempotent, no auto-pull)."""
    git.repo(
        name="Clone CCNotify",
        src=CCNOTIFY_REPO,
        dest=str(_home() / CCNOTIFY_CLONE_DIR),
        pull=False,
    )


def install_ccnotify() -> None:
    """Install CCNotify per upstream README, sourcing ccnotify.py from the local clone.

    Upstream README steps (https://github.com/dazuiba/CCNotify):
      1. mkdir -p ~/.claude/ccnotify
      2. ln -f ccnotify.py ~/.claude/ccnotify/  (we use a symlink to the clone)
      3. chmod a+x ~/.claude/ccnotify/ccnotify.py
      4. brew install terminal-notifier (separate step)

    Hooks in settings.json are intentionally NOT wired here — the user already
    edits ~/.claude/settings.json via chezmoi, and may have a customized version.
    See README "Configure Claude Hooks" for the JSON snippet to add manually.
    """
    home = _home()
    install_dir = home / CCNOTIFY_INSTALL_DIR
    clone_script = home / CCNOTIFY_CLONE_DIR / "ccnotify.py"
    target = install_dir / "ccnotify.py"

    server.shell(
        name="Install CCNotify (mkdir + symlink + chmod)",
        commands=[
            f"mkdir -p {install_dir}",
            # ln -sfn: symlink, force replace, treat existing target as file (not dir).
            # Symlink to the clone so `git pull` in ~/dev/CCNotify updates the install.
            f"ln -sfn {clone_script} {target}",
            f"chmod a+x {target}",
        ],
    )


def install_terminal_notifier() -> None:
    """Install terminal-notifier (CCNotify dependency, macOS only)."""
    brew.packages(
        name="Install terminal-notifier",
        packages=["terminal-notifier"],
        latest=True,
    )


def install_caveman() -> None:
    """Install Caveman plugin per upstream README (https://github.com/juliusbrussee/caveman).

    Two commands from the README "Manual install per agent" section:
      1. claude plugin marketplace add JuliusBrussee/caveman
      2. claude plugin install caveman@caveman
    """
    server.shell(
        name="Install Caveman (marketplace + plugin)",
        commands=[
            f"claude plugin marketplace add {CAVEMAN_MARKETPLACE}",
            f"claude plugin install {CAVEMAN_PLUGIN}",
        ],
    )
