"""Rust: ensure stable + nightly toolchains and install cargo utilities.

rustup-init comes from Brewfile. The garden task already invokes
`rustup default stable` to bootstrap the stable toolchain + cargo. This
task adds the nightly toolchain and a list of cargo binaries.
"""

from pyinfra.operations import server
from shared import home_path, make_env

_ENV = make_env(home_path(".cargo/bin"))

_CARGO_BINARIES = [
    "cargo-update",
    "cargo-workspaces",
    "tailspin",
]

# Rust binaries installed from source (no PyPI/crates.io release).
_CARGO_GIT_REPOS = [
    # https://github.com/gnprice/toml-cli
    "https://github.com/gnprice/toml-cli",
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

for _repo in _CARGO_GIT_REPOS:
    server.shell(
        name=f"cargo install --git {_repo}",
        commands=[f"cargo install --quiet --git {_repo}"],
        _env=_ENV,
    )
