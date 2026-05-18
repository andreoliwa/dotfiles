"""Rust: ensure stable + nightly toolchains and install cargo utilities.

rustup-init comes from Brewfile. The garden task already invokes
`rustup default stable` to bootstrap the stable toolchain + cargo. This
task adds the nightly toolchain and a list of cargo binaries.
"""

from pyinfra.operations import server

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"$HOME/.cargo/bin:{_BREW_PATH}:/usr/bin:/bin"}

_CARGO_BINARIES = [
    "cargo-update",
    "cargo-workspaces",
    "eza",
    "tailspin",
]

server.shell(
    name="rustup install nightly",
    commands=["rustup toolchain install nightly --no-self-update"],
    _env=_ENV,
)

for _pkg in _CARGO_BINARIES:
    server.shell(
        name=f"cargo install {_pkg}",
        commands=[f"cargo install --quiet --locked {_pkg}"],
        _env=_ENV,
    )
