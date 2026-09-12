# Copyright 2026

"""Install managed Python on macOS and Ubuntu, leaving OSMC unchanged."""

from pathlib import Path

from pyinfra.facts.server import Home, Kernel, LinuxName
from pyinfra.operations import apt, files
from shared import home_path, make_env, shell

from pyinfra import host

_IS_DARWIN = host.get_fact(Kernel) == "Darwin"
_IS_UBUNTU = host.get_fact(LinuxName) == "Ubuntu"
_ENV = make_env(home_path(".local/bin"))

# Pyenv is retired on the platforms that now use Mise. OSMC stays untouched,
# because its Raspberry Pi provisioning has separate architecture constraints.
# Historical note: OSMC formerly pre-cloned Pyenv to work around a 32-bit ARM
# Mise/gix bytesize panic (https://github.com/jdx/mise/issues). Do not restore
# that workaround: this task now deliberately leaves OSMC and Pyenv alone.
if _IS_DARWIN or _IS_UBUNTU:
    _HOME = Path(host.get_fact(Home))
    files.directory(
        name="Remove retired Pyenv installation",
        path=str(_HOME / ".pyenv"),
        present=False,
    )
    files.directory(
        name="Remove retired Pyenv Mise cache",
        path=str(_HOME / ".cache" / "mise" / "python" / "pyenv"),
        present=False,
    )

if _IS_UBUNTU:
    apt.packages(
        name="Install system Python and virtual-environment support",
        packages=["python-is-python3", "python3-venv"],
        update=True,
        _sudo=True,
    )

if _IS_DARWIN or _IS_UBUNTU:
    shell(
        name="Install Python versions via mise",
        commands=["mise install python"],
        # PyInfra shells are non-interactive, so shell-function activation is unavailable.
        _env=_ENV,
    )
