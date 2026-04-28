"""Dotfiles manager. Installs and applies server-specific chezmoi source."""

import os
from pathlib import Path

from pyinfra.connectors.local import LocalConnector
from pyinfra.facts.server import Kernel
from pyinfra.operations import brew, files, server

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install chezmoi",
        packages=["chezmoi"],
        latest=True,
    )
else:
    # get.chezmoi.io mis-detects armv7l as "arm" and fetches a 404 URL.
    # Install directly from the GitHub release .deb using the dpkg architecture name.
    server.shell(
        name="Install chezmoi via deb",
        commands=[
            "ARCH=$(dpkg --print-architecture) &&"
            " VER=$(curl -fsLS https://api.github.com/repos/twpayne/chezmoi/releases/latest"
            '  | grep \'"tag_name"\' | head -1 | sed \'s/.*"v\\([^"]*\\)".*/\\1/\') &&'
            " curl -fsSL https://github.com/twpayne/chezmoi/releases/download/v${VER}"
            "/chezmoi_${VER}_linux_${ARCH}.deb -o /tmp/chezmoi.deb &&"
            " sudo dpkg -i /tmp/chezmoi.deb &&"
            " rm /tmp/chezmoi.deb"
        ],
    )

# For local hosts, dotf chezmoi (apply_chezmoi in ops.py) handles application.
# For remote hosts, upload a chezmoi archive and apply it with the remote chezmoi.
if not isinstance(host.connector, LocalConnector):
    _private_repo = os.environ.get("DOTF_REPO", "")
    # host.groups contains the inventory variable name (e.g. "rpi").
    # The first non-"all" group is the server name mapping to chezmoi/<server>/.
    _server_name = next((g for g in host.groups if g != "all"), None)

    if _private_repo and _server_name:
        _chezmoi_src = Path(_private_repo) / "chezmoi" / _server_name
        if _chezmoi_src.is_dir():
            # Build the archive locally at prepare time — small and fast.
            import subprocess
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as _f:
                _archive_name = _f.name
            subprocess.run(  # noqa: S603
                ["chezmoi", "archive", f"--source={_chezmoi_src}", "--output", _archive_name],  # noqa: S607
                check=True,
            )

            files.put(
                name="Upload chezmoi source archive",
                src=_archive_name,
                dest="/tmp/chezmoi-src.tar",  # noqa: S108
            )

            server.shell(
                name="Apply chezmoi from archive",
                commands=["chezmoi apply --source=/tmp/chezmoi-src.tar && rm /tmp/chezmoi-src.tar"],
            )
