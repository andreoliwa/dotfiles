"""Install garden-rs via cargo, then run `garden grow` against ~/.config/garden/garden.yaml.

Prerequisites:

- rustup (from Brewfile) -> stable toolchain -> cargo on PATH.
- ~/.config/garden/garden.yaml deployed via chezmoi (private overlay).
"""

from constants import make_env
from pyinfra.operations import server

_ENV = make_env("$HOME/.cargo/bin")

server.shell(
    name="rustup default stable",
    commands=["rustup default stable >/dev/null 2>&1 || rustup-init -y --no-modify-path --default-toolchain stable"],
    _env=_ENV,
)

server.shell(
    name="cargo install garden-tools",
    commands=["cargo install --quiet --locked garden-tools"],
    _env=_ENV,
)

server.shell(
    name="cargo install fren",
    commands=["cargo install --quiet --locked fren"],
    _env=_ENV,
)

server.shell(
    name="garden grow",
    commands=[
        # Use whatever garden config the user has under ~/.config/garden/.
        # Wildcard '*' grows every tree in the config.
        "for cfg in $HOME/.config/garden/*.yaml $HOME/.config/garden/garden.yaml; do "
        '[ -f "$cfg" ] && garden --config "$cfg" grow \'*\' || true; '
        "done",
    ],
    _env=_ENV,
    _ignore_errors=True,
)
