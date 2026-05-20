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
    name="rustup default stable",
    # Bootstrap stable toolchain so cargo lands in ~/.cargo/bin. If stable is
    # already the default this is a fast no-op; otherwise it initialises the
    # toolchain via rustup-init (installed by brew).
    commands=["rustup default stable >/dev/null 2>&1 || rustup-init -y --no-modify-path --default-toolchain stable"],
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
