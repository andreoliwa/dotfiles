"""Remote-server bootstrap: apt packages + Garden-managed clones on Linux hosts.

OSMC-specific bits (CIFS mounts, samba, video subtitle setup) are not yet
migrated; run them via `dotf legacy` for now.
"""

from pyinfra.facts.server import Kernel
from pyinfra.operations import apt, files, server

from pyinfra import host

_APT_PACKAGES = [
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
    apt.packages(
        name="Install base apt packages",
        packages=_APT_PACKAGES,
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
