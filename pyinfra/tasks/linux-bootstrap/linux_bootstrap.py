# Copyright 2026

"""Install common Linux and OSMC-specific bootstrap dependencies."""

import json

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, files
from shared import home_path, shell

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

# FFsubsync needs these system libraries when it is installed on OSMC.
_OSMC_BOOTSTRAP_APT_PACKAGES = [
    "build-essential",
    "ffmpeg",
    "gcc",
    "git",
    "libffi-dev",
    "libssl-dev",
    "libxml2-dev",
    "libxslt-dev",
    "libxslt1-dev",
    "python3-dev",
    "python3-lxml",
    "python3-numpy",
    "python3-setuptools",
    "python3-wheel",
]

# OSMC needs these groups for framebuffer, audio, and disk device access.
# https://discourse.osmc.tv/t/sad-face-loop-open-dev-fb0-permission-denied/87539
_OSMC_GROUPS = ["osmc", "adm", "disk", "lp", "dialout", "cdrom", "audio", "video"]

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
        path=home_path("OneDrive/Backup"),
    )

    # bash-powerline: https://github.com/riobard/bash-powerline (RPi + Hetzner only)
    shell(
        name="Download bash-powerline.sh",
        commands=[
            (
                "curl -fsSL -o $HOME/.bash-powerline.sh "
                "https://raw.githubusercontent.com/riobard/bash-powerline/master/bash-powerline.sh"
            ),
        ],
    )

    # Link GNU gdate so scripts portable from macOS (where coreutils provides
    # gdate) still work on Linux where `date` is already the GNU version.
    # https://stackoverflow.com/questions/15330775/what-does-gdate-mean-in-this-shell-script
    shell(
        name="Symlink /bin/gdate to system date",
        commands=["command -v gdate || ln -s $(command -v date) /bin/gdate"],
        _sudo=True,
    )

if host.get_fact(LinuxName) == "OSMC":
    shell(
        name="Add osmc user to required groups",
        commands=[f"usermod -aG {','.join(_OSMC_GROUPS)} osmc"],
        _sudo=True,
    )

    apt.packages(
        name="Install OSMC bootstrap packages",
        packages=_OSMC_BOOTSTRAP_APT_PACKAGES,
        update=True,
        _sudo=True,
    )
