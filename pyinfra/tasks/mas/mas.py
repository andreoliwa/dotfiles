"""Mac App Store packages.

`mas` itself comes from Brewfile.common. Lists live in mas_common.toml plus
a variant file (mas_company.toml by default, mas_personal.toml when
Server.brew_variant == "personal").
"""

import tomllib
from pathlib import Path

from pyinfra.facts.server import Kernel
from pyinfra.operations import server

from pyinfra import host

HERE = Path(__file__).parent
_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"{_BREW_PATH}:/usr/bin:/bin"}


def _load(name: str) -> dict:
    return tomllib.loads((HERE / name).read_text())


if host.get_fact(Kernel) == "Darwin":
    _variant = host.data.get("brew_variant", "company")
    _common = _load("mas_common.toml")
    _variant_data = _load(f"mas_{_variant}.toml")

    _install_ids = [*_common.get("install", []), *_variant_data.get("install", [])]
    _remove_ids = [*_common.get("remove", []), *_variant_data.get("remove", [])]

    for _pkg in _install_ids:
        server.shell(
            name=f"mas install {_pkg}",
            commands=[f"mas install {_pkg}"],
            _env=_ENV,
            _ignore_errors=True,
        )

    for _pkg in _remove_ids:
        server.shell(
            name=f"mas uninstall {_pkg}",
            commands=[f"sudo mas uninstall {_pkg}"],
            _env=_ENV,
            _ignore_errors=True,
        )
