"""Shared constants for pyinfra task modules.

Tasks import via the same sys.path injection that lib.py uses (deploy.py
inserts the pyinfra dir into sys.path before running tasks).
"""

# brew lives in /opt/homebrew on Apple Silicon, /usr/local on Intel Macs,
# /home/linuxbrew/.linuxbrew on Linux.
BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"

# Standard system bins. Kept separate so callers can decide ordering.
_SYSTEM_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"


def make_env(*prepend_paths: str) -> dict[str, str]:
    """Return a `_env` dict with PATH = <prepend>:BREW_PATH:<system>.

    Each prepend path is added in order before BREW_PATH. Use for task-specific
    install dirs ($HOME/.cargo/bin, $HOME/.local/bin, mise shims, etc.).
    """
    parts = [*prepend_paths, BREW_PATH, _SYSTEM_PATH]
    return {"PATH": ":".join(parts)}
