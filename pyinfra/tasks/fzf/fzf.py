"""fzf: install via brew on macOS, then run key-bindings + completion installer."""

from pyinfra.facts.server import Kernel
from pyinfra.operations import brew
from shared import make_env, shell

from pyinfra import host

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install fzf",
        packages=["fzf"],
        latest=True,
    )
    shell(
        name="fzf install (key bindings + completion)",
        commands=[
            '"$(brew --prefix)/opt/fzf/install" --key-bindings --completion --no-update-rc',
        ],
        _env=_ENV,
    )
