"""fzf: assumes brew installed it (Brewfile), runs the key-bindings installer."""

from pyinfra.facts.server import Kernel
from pyinfra.operations import server

from pyinfra import host

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"{_BREW_PATH}:/usr/bin:/bin"}

if host.get_fact(Kernel) == "Darwin":
    server.shell(
        name="fzf install (key bindings + completion)",
        commands=[
            '"$(brew --prefix)/opt/fzf/install" --bash --key-bindings --completion --no-update-rc',
        ],
        _env=_ENV,
    )
