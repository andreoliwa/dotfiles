"""Invoke bash completion. Invoke itself is installed via wolt-invoke (pipx)."""

from shared import home_path, make_env, shell

_ENV = make_env(home_path(".local/bin"))

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
