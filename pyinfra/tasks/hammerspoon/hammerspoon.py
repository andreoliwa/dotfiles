"""Hammerspoon: clone Lunette Spoon and symlink into ~/.hammerspoon/Spoons.

Hammerspoon cask + init.lua come from Brewfile + chezmoi respectively.
"""

from pyinfra.facts.server import Kernel
from pyinfra.operations import git, server

from pyinfra import host

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"{_BREW_PATH}:/usr/bin:/bin"}

if host.get_fact(Kernel) == "Darwin":
    server.shell(
        name="Ensure ~/.hammerspoon/Spoons",
        commands=["mkdir -p $HOME/.hammerspoon/Spoons"],
        _env=_ENV,
    )
    git.repo(
        name="Clone Lunette spoon",
        src="https://github.com/scottwhudson/Lunette",
        dest="~/.hammerspoon/Lunette",
        pull=False,
    )
    server.shell(
        name="Symlink Lunette spoon",
        commands=[
            "ln -sfn $HOME/.hammerspoon/Lunette/Source/Lunette.spoon $HOME/.hammerspoon/Spoons/Lunette.spoon",
        ],
        _env=_ENV,
    )
