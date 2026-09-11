# Copyright 2026

"""Install invoke (via pipx) and inject the conjuring task library.

Conjuring is a personal utility library that registers domain-specific invoke
tasks. It is injected as an editable install so local edits to the conjuring
checkout are picked up without reinstalling.

Prerequisites:
    - pipx (python.pipx task) installed.
    - SSH access to GitHub (for the conjuring clone over SSH).
"""

from pyinfra.facts.files import Directory
from pyinfra.facts.server import Kernel
from pyinfra.operations import git
from shared import home_path, make_env, shell

from pyinfra import host

_ENV = make_env(home_path(".local/bin"))
# Login shells can prepend an old pyenv shim before this task runs. Force pipx
# to build its managed environment with the supported system Python on Linux.
_PIPX_ENV = {**_ENV, "PIPX_DEFAULT_PYTHON": "/usr/bin/python3"} if host.get_fact(Kernel) != "Darwin" else _ENV
_CONJURING_PATH = home_path("dev/me/conjuring")

# Uninstall first because `pipx install --force` does not clear the uv-managed
# venv on re-runs (uv refuses to reuse a venv it did not create), causing the
# install to fail with "A virtual environment already exists ... Use `--clear`".
shell(
    name="pipx install invoke",
    commands=[
        "pipx uninstall invoke 2>/dev/null || true; pipx install --force --include-deps invoke",
    ],
    _env=_PIPX_ENV,
)

# Syncthing may provide this source tree without Git metadata. Preserve an
# existing tree so an editable pipx install can use the synchronized files.
if not host.get_fact(Directory, path=_CONJURING_PATH):
    git.repo(
        name="Clone conjuring",
        src="git@github.com:andreoliwa/conjuring.git",
        dest=_CONJURING_PATH,
        pull=False,
    )

shell(
    name="Inject conjuring (editable) into invoke venv",
    commands=[f"pipx inject --force --include-apps -e invoke {_CONJURING_PATH}"],
    _env=_PIPX_ENV,
)

shell(
    name="invoke bash completion",
    commands=[
        (
            "mkdir -p $HOME/.local/share/bash-completion/completions && "
            "invoke --print-completion-script=bash "
            "> $HOME/.local/share/bash-completion/completions/invoke.bash-completion"
        ),
    ],
    _env=_ENV,
    _ignore_errors=True,
)
