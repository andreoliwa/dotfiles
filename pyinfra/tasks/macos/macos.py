"""macOS defaults: run set-defaults.bash from the local files dir."""

from pathlib import Path

from pyinfra.facts.server import Kernel
from pyinfra.operations import files, server

from pyinfra import host

HERE = Path(__file__).parent
_SCRIPT = HERE / "set-defaults.bash"

_DEST = "$HOME/.cache/dotf/set-defaults.bash"

if host.get_fact(Kernel) == "Darwin":
    server.shell(
        name="Ensure dotf cache dir",
        commands=["mkdir -p $HOME/.cache/dotf"],
    )
    files.put(
        name="Sync set-defaults.bash",
        src=str(_SCRIPT),
        dest=_DEST,
        mode="755",
    )
    server.shell(
        name="Run set-defaults.bash",
        commands=[_DEST],
    )
