"""Hammerspoon: install cask, clone Lunette Spoon, symlink into ~/.hammerspoon/Spoons.

Self-contained: installs hammerspoon cask directly so this task can run before
`brew bundle`. init.lua is deployed via chezmoi (private overlay).
"""

from pyinfra.facts.server import Kernel
from pyinfra.operations import brew, git
from shared import home_path, make_env, shell

from pyinfra import host

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    brew.casks(
        name="Install Hammerspoon",
        casks=["hammerspoon"],
        latest=True,
    )
    shell(
        name="Ensure ~/.hammerspoon/Spoons",
        commands=["mkdir -p $HOME/.hammerspoon/Spoons"],
        _env=_ENV,
    )
    git.repo(
        name="Clone Lunette spoon",
        src="https://github.com/scottwhudson/Lunette",
        dest=home_path(".hammerspoon/Lunette"),
        pull=False,
    )
    shell(
        name="Symlink Lunette spoon",
        commands=[
            "ln -sfn $HOME/.hammerspoon/Lunette/Source/Lunette.spoon $HOME/.hammerspoon/Spoons/Lunette.spoon",
        ],
        _env=_ENV,
    )
