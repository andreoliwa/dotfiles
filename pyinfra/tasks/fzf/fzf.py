"""fzf: assumes brew installed it (Brewfile), runs the key-bindings installer."""

from pyinfra.facts.server import Kernel
from pyinfra.operations import server
from shared import make_env

from pyinfra import host

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    server.shell(
        name="fzf install (key bindings + completion)",
        commands=[
            '"$(brew --prefix)/opt/fzf/install" --bash --key-bindings --completion --no-update-rc',
        ],
        _env=_ENV,
    )
