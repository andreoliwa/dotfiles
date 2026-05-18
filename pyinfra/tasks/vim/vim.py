"""vim: install vim-plug plugin manager. Vim itself comes from Brewfile (macvim)."""

from shared import make_env, shell

_ENV = make_env()

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
