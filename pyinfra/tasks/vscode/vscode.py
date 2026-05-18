"""VS Code extensions.

The cask `visual-studio-code` is installed by Brewfile.common. This task
installs every extension listed in extensions.txt via `code --install-extension`.
"""

from pathlib import Path

from constants import make_env
from pyinfra.facts.server import Kernel
from pyinfra.operations import server

from pyinfra import host

HERE = Path(__file__).parent
EXT_FILE = HERE / "extensions.txt"

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    _extensions = [line.strip() for line in EXT_FILE.read_text().splitlines() if line.strip()]
    for _ext in _extensions:
        server.shell(
            name=f"code --install-extension {_ext}",
            commands=[f"code --install-extension {_ext} --force"],
            _env=_ENV,
            _ignore_errors=True,
        )
