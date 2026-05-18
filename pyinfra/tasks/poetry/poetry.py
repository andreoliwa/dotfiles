"""Poetry bash completion. Poetry itself is installed by mise."""

from pyinfra.operations import server

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"$HOME/.local/share/mise/shims:{_BREW_PATH}:/usr/bin:/bin"}

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
