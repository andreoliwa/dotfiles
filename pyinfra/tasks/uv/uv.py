"""Fast Python package and project manager.

Installs uv, then runs `uv tool install --force` for each package in the
server's uv_packages list (from inventory).
"""

import json

from pyinfra.facts.server import Kernel
from pyinfra.operations import brew, server
from shared import home_path, make_env

from pyinfra import host

_ENV = make_env(home_path(".local/bin"))

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install uv",
        packages=["uv"],
        latest=True,
    )
else:
    server.shell(
        name="Install uv via curl",
        commands=["curl -LsSf https://astral.sh/uv/install.sh | sh"],
    )

_pkgs_raw = host.data.get("uv_packages", "[]")
_pkgs = json.loads(_pkgs_raw) if isinstance(_pkgs_raw, str) else _pkgs_raw

_extras_raw = host.data.get("uv_extra_args", "{}")
_extras = json.loads(_extras_raw) if isinstance(_extras_raw, str) else _extras_raw

for _pkg in _pkgs:
    _extra = " ".join(_extras.get(_pkg, []))
    server.shell(
        name=f"uv tool install {_pkg}",
        commands=[f"uv tool install --force {_extra} {_pkg}".strip()],
        _env=_ENV,
    )
