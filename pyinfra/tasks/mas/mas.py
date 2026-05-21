"""Mac App Store packages.

`mas` itself comes from Brewfile.common. Package lists live in meta.toml
under [packages.common] and [packages.<variant>] (company or personal).
"""

import tomllib
from pathlib import Path

from pyinfra.facts.server import Kernel
from shared import make_env, shell, sudo_env

from pyinfra import host

HERE = Path(__file__).parent
_ENV = make_env()
_SUDO_ENV = sudo_env()

if host.get_fact(Kernel) == "Darwin":
    _variant = host.data.get("brew_variant", "company")
    _meta = tomllib.loads((HERE / "meta.toml").read_text())
    _pkgs = _meta.get("packages", {})
    _common = _pkgs.get("common", {})
    _variant_data = _pkgs.get(_variant, {})

    _names = _meta.get("names", {})
    _install_ids = [*_common.get("install", []), *_variant_data.get("install", [])]
    _remove_ids = [*_common.get("remove", []), *_variant_data.get("remove", [])]

    for _pkg in _install_ids:
        _label = _names.get(str(_pkg), str(_pkg))
        shell(
            name=f"mas install {_label}",
            commands=[f"mas install {_pkg}"],
            _env=_ENV,
            _ignore_errors=True,
        )

    for _pkg in _remove_ids:
        _label = _names.get(str(_pkg), str(_pkg))
        shell(
            name=f"mas uninstall {_label}",
            commands=[f"sudo -A mas uninstall {_pkg}"],
            _env=_SUDO_ENV,
            _ignore_errors=True,
        )
