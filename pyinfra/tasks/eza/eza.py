"""eza: install via cargo. Shell aliases ship as a shell.d fragment."""

from constants import make_env
from pyinfra.operations import server

_ENV = make_env("$HOME/.cargo/bin")

server.shell(
    name="cargo install eza",
    commands=["cargo install --quiet --locked eza"],
    _env=_ENV,
)
