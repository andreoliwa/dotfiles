"""Docker / OrbStack bash completions.

OrbStack (cask) is the user's preferred Docker runtime; Docker Desktop
completions are linked only if Docker.app is installed. Both targets are
optional - missing source files are silently skipped.
"""

from pyinfra.facts.server import Kernel
from pyinfra.operations import server

from pyinfra import host

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"{_BREW_PATH}:/usr/bin:/bin"}

if host.get_fact(Kernel) == "Darwin":
    server.shell(
        name="Link docker.bash-completion if Docker.app present",
        commands=[
            "src=/Applications/Docker.app/Contents/Resources/etc/docker.bash-completion; "
            'dst="$(brew --prefix)/etc/bash_completion.d/docker.bash-completion"; '
            '[ -f "$src" ] && ln -sfn "$src" "$dst" || true',
        ],
        _env=_ENV,
    )
    server.shell(
        name="Link docker-compose.bash-completion if Docker.app present",
        commands=[
            "src=/Applications/Docker.app/Contents/Resources/etc/docker-compose.bash-completion; "
            'dst="$(brew --prefix)/etc/bash_completion.d/docker-compose.bash-completion"; '
            '[ -f "$src" ] && ln -sfn "$src" "$dst" || true',
        ],
        _env=_ENV,
    )
