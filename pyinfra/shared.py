"""Shared helpers for pyinfra task modules.

Tasks import via the same sys.path injection that lib.py uses (deploy.py
inserts the pyinfra dir into sys.path before running tasks).
"""

from pyinfra.facts.server import Home
from pyinfra.operations import server as _server

from pyinfra import host

# brew lives in /opt/homebrew on Apple Silicon, /usr/local on Intel Macs,
# /home/linuxbrew/.linuxbrew on Linux.
BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"

# Standard system bins. Kept separate so callers can decide ordering.
_SYSTEM_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"


def brew_bin() -> str:
    """Return the absolute path to the brew binary for the target host."""
    from pyinfra.facts.server import Kernel

    return "/opt/homebrew/bin/brew" if host.get_fact(Kernel) == "Darwin" else "/home/linuxbrew/.linuxbrew/bin/brew"


def make_env(*prepend_paths: str) -> dict[str, str]:
    """Return a `_env` dict with PATH = <prepend>:BREW_PATH:<system>.

    Each prepend path is added in order before BREW_PATH. Use for task-specific
    install dirs ($HOME/.cargo/bin, $HOME/.local/bin, mise shims, etc.).
    """
    parts = [*prepend_paths, BREW_PATH, _SYSTEM_PATH]
    return {"PATH": ":".join(parts)}


def home_path(*parts: str) -> str:
    """Build an absolute path under the remote user's home.

    Use this for any pyinfra op that does NOT expand tilde - notably
    `files.put(dest=...)`. The Home fact resolves on the target host, so the
    path is correct for both local and remote provisioning.
    """
    return "/".join([host.get_fact(Home), *parts])


# Path where brew.py installs the askpass helper (see tasks/brew/askpass.sh).
# Tasks that run `sudo -A` must pass `sudo_env()` so the helper is found.
ASKPASS_PATH = ".local/bin/dotf-askpass.sh"


def sudo_env(*prepend_paths: str) -> dict[str, str]:
    """Return `_env` with PATH + SUDO_ASKPASS for non-TTY `sudo -A` calls.

    pyinfra runs commands without a TTY, so plain `sudo` hangs on the password
    prompt. Use `sudo -A <cmd>` with this env so sudo reads the password from
    the askpass helper (GUI prompt first run, login-keychain cache after).

    Requires tasks/brew/brew.py to have installed the helper first; brew runs
    early in the inventory, so any later task can rely on it being present.
    """
    return {**make_env(*prepend_paths), "SUDO_ASKPASS": home_path(ASKPASS_PATH)}


# Single log file all `shell()` ops append to; follow with `dotf tail`.
PROVISION_LOG = ".cache/dotf/provision.log"


def install_dmg(name: str, url: str, app: str, volume: str | None = None) -> object:
    """Download a DMG, copy the .app to /Applications, then unmount and clean up.

    Idempotent: skips if /Applications/<app>.app already exists.

    Args:
        name:   Human-readable op name (passed to shell()).
        url:    Direct download URL for the .dmg file.
        app:    App bundle name without .app suffix (e.g. "FreeFlow").
        volume: Volume name the DMG mounts as. Defaults to `app`.

    """
    vol = volume or app
    app_path = f"/Applications/{app}.app"
    dmg_tmp = f"${{TMPDIR:-/tmp}}/{app}.dmg"
    return shell(
        name=name,
        commands=(
            f"if [ -d {app_path} ]; then echo '{app} already installed, skipping'; else"
            f" curl -fsSL {url} -o {dmg_tmp}"
            f" && hdiutil attach -nobrowse -quiet {dmg_tmp}"
            f" && cp -R /Volumes/{vol}/{app}.app {app_path}"
            f" && hdiutil detach -quiet /Volumes/{vol}"
            f" && rm {dmg_tmp}; fi"
        ),
    )


def shell(name: str, commands: str | list[str], **kwargs: object) -> object:
    """Wrap `server.shell` so stdout/stderr also append to ~/.cache/dotf/provision.log.

    Use this in place of `server.shell(...)` in any task that runs shell
    commands. The log file is shared by every task, so `dotf tail` follows
    progress across the whole `dotf provision` run.

    Implementation:
      - Joins multiple commands with `&&` so a failure short-circuits.
      - Pipes combined stdout+stderr through tee --append to the log.
      - Wraps in bash to use pipefail so the tee still fails on command error.
    """
    log = home_path(PROVISION_LOG)
    cmd_str = commands if isinstance(commands, str) else " && ".join(commands)

    wrapped = (
        f'mkdir -p "$(dirname {log})" && '
        f'{{ printf "\\n>>> %s\\n" {name!r} >> {log}; }} && '
        f"set -o pipefail; "
        f"({cmd_str}) 2>&1 | tee -a {log}"
    )
    kwargs.setdefault("_shell_executable", "bash")
    return _server.shell(name=name, commands=[wrapped], **kwargs)
