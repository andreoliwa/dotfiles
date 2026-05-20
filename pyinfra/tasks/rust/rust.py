"""Rust: bootstrap stable + nightly toolchains and install cargo utilities.

Installs rustup directly via `brew install rustup` so this task is
self-contained and can run before `brew bundle`. Steps:
  1. Sets up the stable toolchain (puts cargo into ~/.cargo/bin).
  2. Adds the nightly toolchain.
  3. Installs the cargo binaries listed below.

Must run BEFORE any other task that uses cargo (garden, etc.).
"""

from pyinfra.operations import brew
from shared import home_path, make_env, shell

_ENV = make_env(home_path(".cargo/bin"))

brew.packages(
    name="Install rustup",
    packages=["rustup"],
    latest=True,
)

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

shell(
    name="rustup install stable",
    # Three steps because the brew rustup formula (>= 1.28) does NOT create
    # the cargo/rustc proxy symlinks in ~/.cargo/bin/ automatically:
    #   1. `rustup toolchain install` downloads stable into ~/.rustup/toolchains/.
    #   2. `rustup default stable` sets it as the active toolchain.
    #   3. `rustup-init -y --no-modify-path --default-toolchain none` is the
    #      only step that populates ~/.cargo/bin/ with `cargo`, `rustc`, etc.
    #      (proxies that dispatch to the active toolchain). Without it,
    #      `cargo` is not on PATH and later `cargo install` steps fail.
    commands=[
        "rustup toolchain install stable --no-self-update",
        "rustup default stable",
        "/opt/homebrew/opt/rustup/bin/rustup-init -y --no-modify-path --default-toolchain none",
    ],
    _env=_ENV,
)

shell(
    name="rustup install nightly",
    commands=["rustup toolchain install nightly --no-self-update"],
    _env=_ENV,
)

for _pkg in _CARGO_BINARIES:
    shell(
        name=f"cargo install {_pkg}",
        commands=[f"cargo install --quiet --locked {_pkg}"],
        _env=_ENV,
    )

for _repo in _CARGO_GIT_REPOS:
    shell(
        name=f"cargo install --git {_repo}",
        commands=[f"cargo install --quiet --git {_repo}"],
        _env=_ENV,
    )
