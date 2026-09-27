# Copyright 2026

"""Fast Python package and project manager.

Installs uv, then runs `uv tool install --force` for each package in the
server's uv_packages list (from inventory).
"""

import json
import shlex

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import brew
from shared import (
    SYSTEM_PYTHON_EXECUTABLE,
    UV_MANAGED_PYTHON_REQUEST,
    home_path,
    make_env,
    shell,
    system_python_label,
    uv_managed_python_label,
)

from pyinfra import host

_IS_DARWIN = host.get_fact(Kernel) == "Darwin"
_IS_OSMC = host.get_fact(LinuxName) == "OSMC"
_ENV = make_env(home_path(".local/bin"))
# Ubuntu uses its current system interpreter; OSMC must use uv's latest managed interpreter.
_TOOL_ENV = {**_ENV, "UV_PYTHON": SYSTEM_PYTHON_EXECUTABLE} if not _IS_DARWIN and not _IS_OSMC else _ENV
_TOOL_PYTHON_LABEL = (
    uv_managed_python_label() if _IS_OSMC else system_python_label() if not _IS_DARWIN else "uv-selected Python"
)

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install uv",
        packages=["uv"],
        latest=True,
    )
else:
    # Chezmoi owns shell profiles, so prevent uv from re-adding its env source line.
    shell(
        name="Install uv via curl",
        commands=["curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh"],
    )

if _IS_OSMC:
    # OSMC's system Python is too old for Subliminal; use the configured managed interpreter.
    shell(
        name=f"Install {uv_managed_python_label()} on OSMC",
        commands=[f"uv python install {UV_MANAGED_PYTHON_REQUEST}"],
        _env=_ENV,
    )

_pkgs_raw = host.data.get("uv_packages", "[]")
_pkgs = json.loads(_pkgs_raw) if isinstance(_pkgs_raw, str) else _pkgs_raw

_extras_raw = host.data.get("uv_extra_args", "{}")
_extras = json.loads(_extras_raw) if isinstance(_extras_raw, str) else _extras_raw

for _pkg in _pkgs:
    # Preserve version operators in extra requirements, such as "numpy<2.5", as one shell argument.
    _extra = shlex.join(_extras.get(_pkg, []))
    shell(
        name=f"uv tool install {_pkg} ({_TOOL_PYTHON_LABEL})",
        commands=[f"uv tool install --force {_extra} {shlex.quote(_pkg)}".strip()],
        _env=_TOOL_ENV,
    )
