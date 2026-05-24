"""Go: install go via brew, then binaries via `go install` and golangci-lint via mise."""

from pyinfra.operations import brew
from shared import home_path, make_env, shell

brew.packages(
    name="Install go",
    packages=["go"],
    latest=True,
)

_MISE_ENV = make_env(home_path(".local/share/mise/shims"))
_ENV = make_env(home_path("go/bin"))

shell(
    name="mise install golangci-lint",
    commands=["mise install golangci-lint"],
    _env=_MISE_ENV,
)

_BINARIES = [
    "github.com/ianlewis/todos/cmd/todos@latest",
]

for _bin in _BINARIES:
    shell(
        name=f"go install {_bin}",
        commands=[f"go install {_bin}"],
        _env=_ENV,
    )
