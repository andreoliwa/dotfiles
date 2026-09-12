# Copyright 2026

"""Install eza from the platform-native upstream distribution.

macOS uses Homebrew. Ubuntu uses eza's signed apt repository. OSMC uses the
official ARM release because it has a distinct Raspberry Pi architecture and
does not load the shared shell PATH layer; its binary goes in /usr/local/bin.
The eza shell aliases are deployed separately by `20-alias.sh` where shell.d
is enabled.
Reference: https://github.com/eza-community/eza/blob/main/INSTALL.md
"""

from pathlib import Path

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, brew, files
from shared import shell

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install eza",
        packages=["eza"],
        latest=True,
    )
elif host.get_fact(LinuxName) == "Ubuntu":
    apt.packages(
        name="Install eza apt repository prerequisites",
        packages=["ca-certificates", "curl", "gpg"],
        update=True,
        _sudo=True,
    )
    files.directory(
        name="Create apt keyring directory",
        path="/etc/apt/keyrings",
        _sudo=True,
    )
    shell(
        name="Install eza apt repository key",
        commands=[
            (
                "curl -fsSL https://raw.githubusercontent.com/eza-community/eza/main/deb.asc "
                "| gpg --batch --yes --dearmor -o /etc/apt/keyrings/gierens.gpg"
            ),
        ],
        _sudo=True,
    )
    files.put(
        name="Configure eza apt repository",
        src=str(Path(__file__).parent / "gierens.list"),
        dest="/etc/apt/sources.list.d/gierens.list",
        mode="644",
        _sudo=True,
    )
    apt.packages(
        name="Install eza",
        packages=["eza"],
        update=True,
        latest=True,
        _sudo=True,
    )
elif host.get_fact(LinuxName) == "OSMC":
    apt.packages(
        name="Install eza download prerequisite",
        packages=["curl"],
        update=True,
        _sudo=True,
    )
    shell(
        name="Install eza ARM release in /usr/local/bin",
        commands=[
            (
                'case "$(uname -m)" in '
                'aarch64) target="aarch64-unknown-linux-gnu" ;; '
                'armv6l|armv7l) target="arm-unknown-linux-gnueabihf" ;; '
                '*) echo "Unsupported eza architecture: $(uname -m)" >&2; exit 1 ;; esac; '
                'curl -fsSL "https://github.com/eza-community/eza/releases/latest/download/eza_${target}.tar.gz" '
                "| tar -xz -C /usr/local/bin eza"
            ),
        ],
        _sudo=True,
    )
