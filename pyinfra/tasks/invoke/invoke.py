"""Install invoke (via pipx) and inject the conjuring task library.

Conjuring is a personal utility library that registers domain-specific invoke
tasks. It is injected as an editable install so local edits to the conjuring
checkout are picked up without reinstalling.

Prerequisites:
    - pipx (python.pipx task) installed.
    - SSH access to GitHub (for the conjuring clone over SSH).
"""

from pyinfra.operations import git
from shared import home_path, make_env, shell

_ENV = make_env(home_path(".local/bin"))
_CONJURING_PATH = home_path("dev/me/conjuring")

# Uninstall first because `pipx install --force` does not clear the uv-managed
# venv on re-runs (uv refuses to reuse a venv it did not create), causing the
# install to fail with "A virtual environment already exists ... Use `--clear`".
shell(
    name="pipx install invoke",
    commands=[
        "pipx uninstall invoke 2>/dev/null || true; "
        "pipx install --force --include-deps invoke",
    ],
    _env=_ENV,
)

git.repo(
    name="Clone conjuring",
    src="git@github.com:andreoliwa/conjuring.git",
    dest=_CONJURING_PATH,
    pull=False,
)

shell(
    name="Inject conjuring (editable) into invoke venv",
    commands=[f"pipx inject --force -e invoke {_CONJURING_PATH}"],
    _env=_ENV,
)

shell(
    name="invoke bash completion",
    commands=[
        "mkdir -p $HOME/.local/share/bash-completion/completions && "
        "invoke --print-completion-script=bash "
        "> $HOME/.local/share/bash-completion/completions/invoke.bash-completion",
    ],
    _env=_ENV,
    _ignore_errors=True,
)
