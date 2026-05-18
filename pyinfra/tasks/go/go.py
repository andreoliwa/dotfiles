"""Go binaries installed via `go install`. go itself comes from Brewfile."""

from pyinfra.operations import server

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"$HOME/go/bin:{_BREW_PATH}:/usr/bin:/bin"}

_BINARIES = [
    "github.com/ianlewis/todos@latest",
]

for _bin in _BINARIES:
    server.shell(
        name=f"go install {_bin}",
        commands=[f"go install {_bin}"],
        _env=_ENV,
    )
