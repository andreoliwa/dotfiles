"""Deploy Python tooling: pipx install and module management.

Python versions are managed by mise (chezmoi/dot_config/mise/config.toml).
This task handles pipx and the pipx-installed modules from pipx.toml.
"""

import os
import tomllib
from pathlib import Path

from pyinfra.operations import server

IS_COMPANY_LAPTOP = bool(os.environ.get("COMPANY_LAPTOP"))

_PIPX = tomllib.loads((Path(__file__).parent / "pipx.toml").read_text())

# -- Python versions -----------------------------------------------------------

server.shell(
    name="Install Python versions via mise",
    commands=["mise install python"],
)

# -- pipx itself ---------------------------------------------------------------

server.shell(
    name="Install pipx via pip",
    commands=["python3 -m pip install -U --user pipx"],
)

server.shell(
    name="Ensure pipx is on PATH",
    commands=["pipx ensurepath"],
    _ignore_errors=True,
)

# -- uninstall removed modules -------------------------------------------------

_remove = list(_PIPX.get("remove", []))
if IS_COMPANY_LAPTOP:
    _remove += _PIPX.get("personal_laptop", [])
else:
    _remove += _PIPX.get("company_laptop", [])

for _pkg in _remove:
    server.shell(
        name=f"pipx uninstall {_pkg}",
        commands=[f"pipx uninstall {_pkg}"],
        _ignore_errors=True,
    )

# -- install modules -----------------------------------------------------------

_install = list(_PIPX.get("common", []))
if IS_COMPANY_LAPTOP:
    _install += _PIPX.get("company_laptop", [])
else:
    _install += _PIPX.get("personal_laptop", [])

for _pkg in _install:
    server.shell(
        name=f"pipx install {_pkg}",
        commands=[f"pipx install --verbose {_pkg}"],
        _ignore_errors=True,
    )
