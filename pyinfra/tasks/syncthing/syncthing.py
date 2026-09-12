# Copyright 2026

"""Install Syncthing with Homebrew on macOS and its official apt repo on Ubuntu.

macOS installs the `syncthing-app` cask, the renamed GUI app previously owned
by the common Brewfile. Ubuntu uses Syncthing's stable-v2 apt repository and
enables the packaged per-user service for the desktop user.
Reference: https://apt.syncthing.net/
"""

from pathlib import Path

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, brew, files
from shared import shell

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.casks(
        name="Install Syncthing.app",
        casks=["syncthing-app"],
        latest=True,
    )
elif host.get_fact(LinuxName) == "Ubuntu":
    apt.packages(
        name="Install Syncthing apt repository prerequisites",
        packages=["ca-certificates", "curl"],
        update=True,
        _sudo=True,
    )
    files.directory(
        name="Create apt keyring directory",
        path="/etc/apt/keyrings",
        _sudo=True,
    )
    shell(
        name="Install Syncthing apt repository key",
        commands=[
            "curl -fsSL https://syncthing.net/release-key.gpg -o /etc/apt/keyrings/syncthing-archive-keyring.gpg",
        ],
        _sudo=True,
    )
    files.put(
        name="Configure Syncthing stable apt repository",
        src=str(Path(__file__).parent / "syncthing.list"),
        dest="/etc/apt/sources.list.d/syncthing.list",
        mode="644",
        _sudo=True,
    )
    apt.packages(
        name="Install Syncthing",
        packages=["syncthing"],
        update=True,
        latest=True,
        _sudo=True,
    )
    shell(
        name="Enable Syncthing user service",
        commands=[
            'export XDG_RUNTIME_DIR="/run/user/$(id -u)"; systemctl --user enable --now syncthing.service',
        ],
    )
