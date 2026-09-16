# Copyright 2026
"""fzf: install via Homebrew on macOS and APT on Linux."""

from pyinfra.facts.server import Kernel
from pyinfra.operations import apt, brew
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


if host.get_fact(Kernel) == "Linux":
    apt.packages(
        name="Install fzf",
        packages=["fzf"],
        _sudo=True,
    )
