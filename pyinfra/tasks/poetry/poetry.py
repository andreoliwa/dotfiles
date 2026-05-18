"""Poetry bash completion. Poetry itself is installed by mise."""

from constants import make_env
from pyinfra.operations import server

_ENV = make_env("$HOME/.local/share/mise/shims")

server.shell(
    name="Remove legacy ~/.poetry dir",
    commands=["rm -rf $HOME/.poetry"],
    _env=_ENV,
    _ignore_errors=True,
)

server.shell(
    name="poetry bash completion",
    commands=[
        "mkdir -p $HOME/.local/share/bash-completion/completions && "
        "poetry completions bash > $HOME/.local/share/bash-completion/completions/poetry.bash-completion",
    ],
    _env=_ENV,
    _ignore_errors=True,
)
