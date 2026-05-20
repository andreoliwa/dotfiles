"""Git: install gh CLI + set global gpg.format default.

gh is installed directly via brew formula so this task is self-contained
and can run before `brew bundle`. Identity, signing key, and gpgsign flags
are configured per-profile in chezmoi (private gitconfig overlay).
"""

from pyinfra.operations import brew
from shared import make_env, shell

_ENV = make_env()

brew.packages(
    name="Install gh",
    packages=["gh"],
    latest=True,
)

shell(
    name="git config: gpg.format openpgp",
    commands=["git config --global gpg.format openpgp"],
    _env=_ENV,
)
