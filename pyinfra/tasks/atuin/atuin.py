"""atuin shell history: install via the official script.

Shell fragment lives in 99-init.sh in this same dir.
Reference: https://docs.atuin.sh/guide/installation/
"""

from pyinfra.operations import server
from shared import home_path, make_env

_ENV = make_env(home_path(".atuin/bin"))

server.shell(
    name="Install atuin",
    commands=[
        "command -v atuin >/dev/null 2>&1 || curl --proto '=https' --tlsv1.2 -sSf https://setup.atuin.sh | bash",
    ],
    _env=_ENV,
)
