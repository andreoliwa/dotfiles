"""Git: gh CLI + global gpg.format default.

gh comes from Brewfile. Identity, signing key, and gpgsign flags are
configured per-profile in chezmoi (private gitconfig overlay).
"""

from constants import make_env
from pyinfra.operations import server

_ENV = make_env()

server.shell(
    name="git config: gpg.format openpgp",
    commands=["git config --global gpg.format openpgp"],
    _env=_ENV,
)

server.shell(
    name="gh smoke check",
    commands=["gh --version >/dev/null"],
    _env=_ENV,
)
