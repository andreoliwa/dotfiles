# Copyright 2026

"""Install Vim and its plugin manager."""

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, brew
from shared import make_env, shell

from pyinfra import host

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install macvim",
        packages=["macvim"],
        latest=True,
    )
elif host.get_fact(LinuxName) == "Ubuntu":
    apt.packages(
        name="Install vim",
        packages=["vim"],
        update=True,
        _sudo=True,
    )

shell(
    name="Ensure ~/.vim/autoload dir",
    commands=["mkdir -p $HOME/.vim/autoload"],
    _env=_ENV,
)

shell(
    name="Install vim-plug",
    commands=[
        (
            "curl -fsSL -o $HOME/.vim/autoload/plug.vim "
            "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"
        ),
    ],
    _env=_ENV,
)

shell(
    name="vim PlugInstall (non-interactive)",
    commands=["vim -es -u $HOME/.vimrc -i NONE -c 'PlugInstall | qall' || true"],
    _env=_ENV,
    _ignore_errors=True,
)
