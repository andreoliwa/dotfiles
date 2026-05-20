"""Rust: bootstrap stable + nightly toolchains and install cargo utilities.

rustup-init comes from Brewfile (brew formula `rustup`). This task:
  1. Sets up the stable toolchain (puts cargo into ~/.cargo/bin).
  2. Adds the nightly toolchain.
  3. Installs the cargo binaries listed below.

Must run BEFORE any other task that uses cargo (garden, etc.).
"""

from shared import home_path, make_env, shell

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

shell(
    name="rustup install stable",
    # `rustup default stable` only writes a pointer in the rustup config; it
    # does NOT download the toolchain. `rustup toolchain install` is the step
    # that actually downloads stable into ~/.rustup/toolchains/ and places
    # cargo + rustc in ~/.cargo/bin/. Then set stable as default.
    commands=[
        "rustup toolchain install stable --no-self-update",
        "rustup default stable",
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
