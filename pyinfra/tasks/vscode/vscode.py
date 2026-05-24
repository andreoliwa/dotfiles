"""VS Code: install cask then extensions from extensions.txt."""

from pathlib import Path

from pyinfra.facts.server import Kernel
from pyinfra.operations import brew
from shared import make_env, shell

from pyinfra import host

HERE = Path(__file__).parent
EXT_FILE = HERE / "extensions.txt"

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    brew.cask(
        name="Install visual-studio-code",
        src="visual-studio-code",
    )
    _extensions = [line.strip() for line in EXT_FILE.read_text().splitlines() if line.strip()]
    for _ext in _extensions:
        shell(
            name=f"code --install-extension {_ext}",
            commands=[f"code --install-extension {_ext} --force"],
            _env=_ENV,
            _ignore_errors=True,
        )
