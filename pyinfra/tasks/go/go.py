"""Go binaries installed via `go install`. go itself comes from Brewfile."""

from shared import home_path, make_env, shell

_ENV = make_env(home_path("go/bin"))

_BINARIES = [
    "github.com/ianlewis/todos/cmd/todos@latest",
]

for _bin in _BINARIES:
    shell(
        name=f"go install {_bin}",
        commands=[f"go install {_bin}"],
        _env=_ENV,
    )
