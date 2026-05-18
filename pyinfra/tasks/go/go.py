"""Go binaries installed via `go install`. go itself comes from Brewfile."""

from constants import make_env
from pyinfra.operations import server

_ENV = make_env("$HOME/go/bin")

_BINARIES = [
    "github.com/ianlewis/todos@latest",
]

for _bin in _BINARIES:
    server.shell(
        name=f"go install {_bin}",
        commands=[f"go install {_bin}"],
        _env=_ENV,
    )
