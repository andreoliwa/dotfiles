"""Remote-server bootstrap: apt packages + clones on Linux hosts (Hetzner, RPi/OSMC).

Per-host apt packages come from Server.apt_packages in the private inventory.
OSMC-specific bits (group memberships, video-subtitle pipx installs) run only
when LinuxName == "OSMC".
"""

import json

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, files, git
from shared import home_path, make_env, shell

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

# OSMC: ffsubsync wraps several apt-installed dev libraries.
_OSMC_VIDEO_APT_PACKAGES = [
    "build-essential",
    "ffmpeg",
    "gcc",
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

# https://github.com/Diaoul/subliminal
# https://github.com/smacke/ffsubsync
# https://github.com/andreoliwa/python-vidsub
_OSMC_VIDEO_PIPX_PACKAGES = [
    ("subliminal", "git+https://github.com/Diaoul/subliminal.git@develop", False),
    ("ffsubsync", "ffsubsync", True),
    ("vidsub", "git+https://github.com/andreoliwa/python-vidsub", True),
]

# Groups that the osmc user needs so the framebuffer/audio/disk devices work.
# Avoids the "open /dev/fb0: Permission denied" sad-face boot loop.
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

    git.repo(
        name="Clone container-apps",
        src="https://github.com/andreoliwa/container-apps",
        dest=home_path("container-apps"),
        pull=True,
    )

    # bash-powerline: https://github.com/riobard/bash-powerline (RPi + Hetzner only)
    shell(
        name="Download bash-powerline.sh",
        commands=[
            "curl -fsSL -o $HOME/.bash-powerline.sh "
            "https://raw.githubusercontent.com/riobard/bash-powerline/master/bash-powerline.sh",
        ],
    )

    # Link GNU gdate so scripts portable from macOS (where coreutils provides
    # gdate) still work on Linux where `date` is already the GNU version.
    # https://stackoverflow.com/questions/15330775/what-does-gdate-mean-in-this-shell-script
    shell(
        name="Symlink /bin/gdate to system date",
        commands=["command -v gdate || sudo ln -s $(command -v date) /bin/gdate"],
    )

if host.get_fact(LinuxName) == "OSMC":
    shell(
        name="Add osmc user to required groups",
        commands=[f"sudo usermod -aG {','.join(_OSMC_GROUPS)} osmc"],
    )

    apt.packages(
        name="Install OSMC video-subtitle apt dependencies",
        packages=_OSMC_VIDEO_APT_PACKAGES,
        update=True,
        _sudo=True,
    )

    _pipx_env = make_env(home_path(".local/bin"))
    for _name, _spec, _system_site in _OSMC_VIDEO_PIPX_PACKAGES:
        _flags = "--system-site-packages " if _system_site else ""
        shell(
            name=f"pipx install {_name}",
            commands=[f"pipx install --force {_flags}{_spec}"],
            _env=_pipx_env,
        )
