"""AI tools: Claude Code add-ons and general AI utilities.

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
from pyinfra.operations import brew, git
from shared import home_path, make_env, shell

from pyinfra import host

CCNOTIFY_REPO = "https://github.com/dazuiba/CCNotify.git"
CCNOTIFY_CLONE_DIR = "dev/CCNotify"
CCNOTIFY_INSTALL_DIR = ".claude/ccnotify"

CAVEMAN_MARKETPLACE = "JuliusBrussee/caveman"
CAVEMAN_PLUGIN = "caveman@caveman"

OMEGA_MEMORY_PACKAGE = "omega-memory[server]"
_OMEGA_ENV = make_env(home_path(".local/bin"))


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

    Hooks in settings.json are intentionally NOT wired here - the user already
    edits ~/.claude/settings.json via chezmoi, and may have a customized version.
    See README "Configure Claude Hooks" for the JSON snippet to add manually.
    """
    home = _home()
    install_dir = home / CCNOTIFY_INSTALL_DIR
    clone_script = home / CCNOTIFY_CLONE_DIR / "ccnotify.py"
    target = install_dir / "ccnotify.py"

    shell(
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
    """Install alerter (CCNotify dependency, macOS only).

    terminal-notifier v2.0.0 (last release 2017) uses NSUserNotificationCenter
    which Apple removed in macOS 14. alerter (vjeantet/alerter) is the
    upstream-recommended replacement using UNUserNotificationCenter.
    See: https://github.com/julienXX/terminal-notifier (README redirects to alerter)
    """
    brew.packages(
        name="Install alerter (terminal-notifier replacement for macOS 14+)",
        packages=["vjeantet/tap/alerter"],
        latest=True,
    )


def install_caveman() -> None:
    """Install Caveman plugin per upstream README (https://github.com/juliusbrussee/caveman).

    Two commands from the README "Manual install per agent" section:
      1. claude plugin marketplace add JuliusBrussee/caveman
      2. claude plugin install caveman@caveman
    """
    shell(
        name="Install Caveman (marketplace + plugin)",
        commands=[
            f"claude plugin marketplace add {CAVEMAN_MARKETPLACE}",
            f"claude plugin install {CAVEMAN_PLUGIN}",
        ],
    )


def install_omega_memory() -> None:
    """Install omega-memory: cross-model persistent memory via MCP, local-first.

    Three steps per upstream llms-install.md (https://github.com/omega-memory/omega-memory):
      1. uv tool install omega-memory[server]     - installs the CLI + MCP server
      2. omega setup --client claude-code         - registers MCP, installs hooks, writes CLAUDE.md;
                                                   may exit 1 if model download 404s (legacy URL)
      3. omega setup --download-model             - downloads bge-small-en-v1.5 (the working model)

    Step 2 uses _ignore_errors=True because omega exits 1 when the bundled model URL 404s, even
    though MCP registration and hooks succeed. Step 3 then fetches the correct model separately.
    Both setup steps are idempotent; re-running is safe.

    MCP registration and hook wiring happen here, not via chezmoi, because omega writes directly
    to ~/.claude/settings.json with client-detected paths.
    """
    shell(
        name=f"uv tool install {OMEGA_MEMORY_PACKAGE}",
        commands=[f"uv tool install --force '{OMEGA_MEMORY_PACKAGE}'"],
        _env=_OMEGA_ENV,
    )
    # _ignore_errors: omega exits 1 when "already registered" on re-runs or when the
    # bundled all-MiniLM-L6-v2 model URL 404s. MCP registration, hooks, and CLAUDE.md
    # are written successfully regardless.
    shell(
        name="omega setup for Claude Code",
        commands=["omega setup --client claude-code"],
        _env=_OMEGA_ENV,
        _ignore_errors=True,
    )
    # Download the working bge-small-en-v1.5 model only if not already complete.
    # Both files required: partial downloads leave model.onnx but miss tokenizer.json.
    # To force re-download: rm -rf ~/.cache/omega/models/bge-small-en-v1.5-onnx
    shell(
        name="omega download bge-small-en-v1.5 model",
        commands=[
            "model_dir=$HOME/.cache/omega/models/bge-small-en-v1.5-onnx"
            ' && echo "omega model dir: $model_dir"'
            ' && echo "  (to force re-download: rm -rf $model_dir)"'
            ' && if [ ! -f "$model_dir/model.onnx" ] || [ ! -f "$model_dir/tokenizer.json" ];'
            " then omega setup --download-model; fi"
        ],
        _env=_OMEGA_ENV,
        _ignore_errors=True,
    )


def install_jeeves() -> None:
    """Install jeeves - TUI for browsing and resuming AI agent sessions.

    Supports Claude Code, Codex, and OpenCode. Run `jeeves` to browse sessions
    or `jeeves <search term>` to filter. Press `r` to resume a session in the agent.

    See: https://github.com/robinovitch61/jeeves
    """
    brew.packages(
        name="Install jeeves",
        packages=["robinovitch61/tap/jeeves"],
        latest=True,
    )
