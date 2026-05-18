"""eza: install via cargo. Shell aliases ship as a shell.d fragment."""

from pyinfra.operations import server

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"$HOME/.cargo/bin:{_BREW_PATH}:/usr/bin:/bin"}

server.shell(
    name="cargo install eza",
    commands=["cargo install --quiet --locked eza"],
    _env=_ENV,
)
