# Copyright 2026

"""Install Starship with Homebrew on macOS and its official installer on Linux.

OSMC uses /usr/local/bin because it does not load shell.d. The `40-init.sh`
fragment initializes Starship wherever the shared Bash configuration is used.
Reference: https://starship.rs/guide/
"""

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, brew
from shared import home_path, make_env, shell

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install Starship",
        packages=["starship"],
        latest=True,
    )
elif host.get_fact(LinuxName) == "OSMC":
    apt.packages(
        name="Install Starship download prerequisite",
        packages=["curl"],
        update=True,
        _sudo=True,
    )
    # OSMC does not load shell.d, so use a system PATH directory for this binary.
    shell(
        name="Install Starship in /usr/local/bin",
        commands=["curl -sS https://starship.rs/install.sh | sh -s -- -y -b /usr/local/bin"],
        _sudo=True,
    )
else:
    shell(
        name="Install Starship in ~/.local/bin",
        commands=['curl -sS https://starship.rs/install.sh | sh -s -- -y -b "$HOME/.local/bin"'],
        _env=make_env(home_path(".local/bin")),
    )
