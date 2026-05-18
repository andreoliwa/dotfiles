"""eza: install via cargo. Shell aliases ship as a shell.d fragment."""

from pyinfra.operations import server
from shared import home_path, make_env

_ENV = make_env(home_path(".cargo/bin"))

server.shell(
    name="cargo install eza",
    commands=["cargo install --quiet --locked eza"],
    _env=_ENV,
)
