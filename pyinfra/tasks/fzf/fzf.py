"""fzf: assumes brew installed it (Brewfile), runs the key-bindings installer."""

from pyinfra.facts.server import Kernel
from shared import make_env, shell

from pyinfra import host

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    shell(
        name="fzf install (key bindings + completion)",
        commands=[
            '"$(brew --prefix)/opt/fzf/install" --key-bindings --completion --no-update-rc',
        ],
        _env=_ENV,
    )
