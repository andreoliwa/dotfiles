# Copyright 2026

"""Install pipx and manage pipx-installed packages from inventory.

Reads ``host.data.pipx_packages`` (list[str]) and ``host.data.pipx_injects``
(dict[str, list[str]]) - both JSON-encoded by Server.to_pyinfra_host().
"""

import json

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, brew
from shared import SYSTEM_PYTHON_EXECUTABLE, home_path, make_env, shell, system_python_label

from pyinfra import host

_ENV = make_env(home_path(".local/bin"))
_PIPX_PYTHON_LABEL = "Homebrew Python" if host.get_fact(Kernel) == "Darwin" else system_python_label()

# macOS and Ubuntu mark their system Python environments as externally managed
# (PEP 668). Use each platform's package manager there; retain the existing
# pip fallback for other Linux platforms.
if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install pipx via brew",
        packages=["pipx"],
        latest=True,
    )
elif host.get_fact(LinuxName) == "Ubuntu":
    apt.packages(
        name="Install pipx via apt",
        packages=["pipx"],
        update=True,
        _sudo=True,
    )
else:
    shell(
        name=f"Install pipx via pip --user ({system_python_label()})",
        commands=[f"{SYSTEM_PYTHON_EXECUTABLE} -m pip install -U --user pipx"],
        _env=_ENV,
    )

shell(
    name=f"Ensure pipx is on PATH ({_PIPX_PYTHON_LABEL})",
    commands=["pipx ensurepath"],
    _env=_ENV,
    _ignore_errors=True,
)


def _decode(raw: object, default: object) -> object:
    if isinstance(raw, str) and raw:
        return json.loads(raw)
    return raw or default


_packages: list[str] = _decode(host.data.get("pipx_packages", "[]"), [])  # type: ignore[assignment]
_injects: dict[str, list[str]] = _decode(host.data.get("pipx_injects", "{}"), {})  # type: ignore[assignment]

for _pkg in _packages:
    shell(
        name=f"pipx install {_pkg} ({_PIPX_PYTHON_LABEL})",
        commands=[f"pipx install --force --include-deps {_pkg}"],
        _env=_ENV,
    )
    for _inject in _injects.get(_pkg, []):
        shell(
            name=f"pipx inject {_pkg} <- {_inject} ({_PIPX_PYTHON_LABEL})",
            commands=[f"pipx inject --force -e {_pkg} {_inject}"],
            _env=_ENV,
        )
