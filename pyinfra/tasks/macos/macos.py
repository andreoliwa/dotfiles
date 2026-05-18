"""macOS defaults: run set-defaults.sh from the local files dir."""

from pathlib import Path

from pyinfra.facts.server import Kernel
from pyinfra.operations import files
from shared import home_path, shell

from pyinfra import host

HERE = Path(__file__).parent
_SCRIPT = HERE / "set-defaults.sh"

_DEST = home_path(".cache/dotf/set-defaults.sh")

if host.get_fact(Kernel) == "Darwin":
    shell(
        name="Ensure dotf cache dir",
        commands=["mkdir -p $HOME/.cache/dotf"],
    )
    files.put(
        name="Sync set-defaults.sh",
        src=str(_SCRIPT),
        dest=_DEST,
        mode="755",
    )
    shell(
        name="Run set-defaults.sh",
        commands=[_DEST],
    )
