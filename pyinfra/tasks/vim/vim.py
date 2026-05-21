"""vim: install macvim via brew on macOS, then install vim-plug plugin manager."""

from pyinfra.facts.server import Kernel
from pyinfra.operations import brew
from shared import make_env, shell

from pyinfra import host

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install macvim",
        packages=["macvim"],
        latest=True,
    )

shell(
    name="Ensure ~/.vim/autoload dir",
    commands=["mkdir -p $HOME/.vim/autoload"],
    _env=_ENV,
)

shell(
    name="Install vim-plug",
    commands=[
        "curl -fsSL -o $HOME/.vim/autoload/plug.vim "
        "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim",
    ],
    _env=_ENV,
)

shell(
    name="vim PlugInstall (non-interactive)",
    commands=["vim -es -u $HOME/.vimrc -i NONE -c 'PlugInstall | qall' || true"],
    _env=_ENV,
    _ignore_errors=True,
)
