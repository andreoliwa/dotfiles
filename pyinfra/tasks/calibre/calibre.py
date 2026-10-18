# Copyright 2026

"""Install Calibre via Homebrew on macOS or the upstream Ubuntu binary installer.

Reference: https://calibre-ebook.com/
Linux installer: https://calibre-ebook.com/download_linux
Ubuntu uses the official installer for current upstream releases and upgrades.
Alternatives: apt manages upgrades but Ubuntu's packages can lag upstream;
Snap manages updates but confines USB/removable-media access behind explicit
connections, with incomplete reader/MTP compatibility testing. Prefer upstream
for current releases and Kindle access without Snap confinement.
Alternatives: https://packages.ubuntu.com/search?keywords=calibre
              https://snapcraft.io/install/calibre/ubuntu
Preserve usable current/newer binaries; upgrade older ones without touching libraries.
"""

import re

from pyinfra.facts.server import Command, Kernel, LinuxName
from pyinfra.operations import apt, brew
from shared import shell

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.casks(
        name="Install Calibre.app",
        casks=["calibre"],
        latest=True,
    )
elif host.get_fact(Kernel) == "Linux" and host.get_fact(LinuxName) == "Ubuntu":
    from urllib.request import urlopen

    # Calibre's own update checker uses this endpoint; resolve on the controller
    # so planning does not require wget or Python to be installed on the target yet.
    with urlopen("https://calibre-ebook.com/latest-version", timeout=20) as response:
        latest_version = response.read().decode("ascii").strip()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", latest_version):
        message = f"Invalid upstream Calibre version: {latest_version!r}"
        raise ValueError(message)
    latest_parts = tuple(map(int, latest_version.split(".")))

    apt.packages(
        name="Install Calibre prerequisites",
        packages=[
            # keep-sorted start
            "ca-certificates",
            "libegl1",
            "libopengl0",
            "libxcb-cursor0",
            "libxcb-xinerama0",
            "python3",
            "wget",
            "xdg-utils",
            "xz-utils",
            # keep-sorted end
        ],
        update=True,
        _sudo=True,
    )
    # A directory, PATH alias, or output from a failed probe is not a usable installation.
    installed = host.get_fact(
        Command,
        command='if version=$(/opt/calibre/calibre --version 2>/dev/null); then printf "%s" "$version"; fi',
    )
    installed_version = re.search(r"\bcalibre ([0-9]+)\.([0-9]+)(?:\.([0-9]+))?(?=[ )]|$)", installed or "")
    installed_parts = tuple(map(int, installed_version.groups(default="0"))) if installed_version else (0, 0, 0)
    if installed_parts < latest_parts:
        shell(
            name="Install or upgrade upstream Calibre binary",
            commands=[
                (
                    'set -eu; installer="$(mktemp)"; '
                    "trap 'rm -f \"$installer\"' EXIT; "
                    'wget -nv -O "$installer" https://download.calibre-ebook.com/linux-installer.sh; '
                    f'sh "$installer" version={latest_version}; '
                    "/opt/calibre/calibre --version"
                ),
            ],
            _sudo=True,
            # A sudo login shell expands installer variables before the inner Bash runs.
            _use_sudo_login=False,
        )
