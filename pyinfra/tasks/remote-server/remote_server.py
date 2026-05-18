"""Remote-server bootstrap: apt packages + Garden-managed clones on Linux hosts.

OSMC-specific bits (CIFS mounts, samba, video subtitle setup) are not yet
migrated; run them via `dotf legacy` for now.

Per-host apt packages come from Server.apt_packages in the private inventory.
"""

import json

from pyinfra.facts.server import Kernel
from pyinfra.operations import apt, files, server

from pyinfra import host

_BASE_APT_PACKAGES = [
    "curl",
    "dos2unix",
    "gnupg-agent",
    "gnupg2",
    "htop",
    "lsof",
    "python3-pip",
    "strace",
    "wget",
]

if host.get_fact(Kernel) == "Linux":
    _raw = host.data.get("apt_packages", "[]")
    _extra = json.loads(_raw) if isinstance(_raw, str) else _raw
    apt.packages(
        name="Install apt packages (base + per-host)",
        packages=_BASE_APT_PACKAGES + list(_extra),
        update=True,
        _sudo=True,
    )
    files.directory(
        name="Ensure ~/OneDrive/Backup",
        path="~/OneDrive/Backup",
    )

    # bash-powerline: https://github.com/riobard/bash-powerline (RPi + Hetzner only)
    server.shell(
        name="Download bash-powerline.sh",
        commands=[
            "curl -fsSL -o $HOME/.bash-powerline.sh "
            "https://raw.githubusercontent.com/riobard/bash-powerline/master/bash-powerline.sh",
        ],
    )

    # Link GNU gdate so scripts portable from macOS (where coreutils provides
    # gdate) still work on Linux where `date` is already the GNU version.
    # https://stackoverflow.com/questions/15330775/what-does-gdate-mean-in-this-shell-script
    server.shell(
        name="Symlink /bin/gdate to system date",
        commands=["command -v gdate || sudo ln -s $(command -v date) /bin/gdate"],
    )
