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
from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import git
from shared import (
    SYSTEM_PYTHON_EXECUTABLE,
    home_path,
    make_env,
    shell,
    system_python_label,
    uv_managed_python_label,
    uv_managed_python_shell_env,
)

from pyinfra import host

_ENV = make_env(home_path(".local/bin"))
_IS_OSMC = host.get_fact(LinuxName) == "OSMC"
# Login shells can prepend an old pyenv shim before this task runs. OSMC's
# system Python is too old for Invoke, so use the uv-managed interpreter there.
if _IS_OSMC:
    _PIPX_ENV = _ENV
    _PIPX_PYTHON_ENV = uv_managed_python_shell_env("PIPX_DEFAULT_PYTHON")
    _PIPX_PYTHON_LABEL = uv_managed_python_label()
elif host.get_fact(Kernel) != "Darwin":
    _PIPX_ENV = {**_ENV, "PIPX_DEFAULT_PYTHON": SYSTEM_PYTHON_EXECUTABLE}
    _PIPX_PYTHON_ENV = ""
    _PIPX_PYTHON_LABEL = system_python_label()
else:
    _PIPX_ENV = _ENV
    _PIPX_PYTHON_ENV = ""
    _PIPX_PYTHON_LABEL = "Homebrew Python"
_CONJURING_PATH = home_path("dev/me/conjuring")

# Uninstall first because `pipx install --force` does not clear the uv-managed
# venv on re-runs (uv refuses to reuse a venv it did not create), causing the
# install to fail with "A virtual environment already exists ... Use `--clear`".
shell(
    name=f"pipx install invoke ({_PIPX_PYTHON_LABEL})",
    commands=[
        (
            f"{_PIPX_PYTHON_ENV} pipx uninstall invoke 2>/dev/null || true; "
            f"{_PIPX_PYTHON_ENV} pipx install --force --include-deps invoke"
        ),
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
    name=f"Inject conjuring (editable) into invoke venv ({_PIPX_PYTHON_LABEL})",
    commands=[f"{_PIPX_PYTHON_ENV} pipx inject --force --include-apps -e invoke {_CONJURING_PATH}"],
    _env=_PIPX_ENV,
)

shell(
    name=f"Initialize Invoke with Conjuring ({_PIPX_PYTHON_LABEL})",
    commands=["conjuring init"],
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
