# Copyright 2026

"""Dotfiles manager. Installs and applies the source assembled by dotf.

Remote apply is intentionally unconditional here: diff preview, source upload,
and user confirmation happen in `src/dotf/ops.py` before PyInfra is invoked.
Only after confirmation does this task run `chezmoi apply --force` against the
already-uploaded `/tmp/chezmoi-src` source. `--force` is required because
PyInfra has no TTY for Chezmoi's target-changed confirmation; the earlier diff
and explicit user confirmation are the safe review point. That source can
combine shared layers and a server-specific override.

For local hosts, dotf handles apply directly and this remote-apply block is
skipped.
"""

import os
from pathlib import Path

from lib import Server
from pyinfra.connectors.local import LocalConnector
from pyinfra.facts.server import Kernel
from pyinfra.operations import apt, brew, files
from shared import shell

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install chezmoi",
        packages=["chezmoi"],
        latest=True,
    )
else:
    # get.chezmoi.io mis-detects armv7l as "arm" and fetches a 404 URL.
    # Download as the SSH user, then let PyInfra perform the privileged install.
    _chezmoi_deb = "/tmp/chezmoi.deb"  # noqa: S108
    shell(
        name="Download chezmoi deb",
        commands=[
            (
                "ARCH=$(dpkg --print-architecture) &&"
                " VER=$(curl -fsLS https://api.github.com/repos/twpayne/chezmoi/releases/latest"
                '  | grep \'"tag_name"\' | head -1 | sed \'s/.*"v\\([^"]*\\)".*/\\1/\') &&'
                " curl -fsSL https://github.com/twpayne/chezmoi/releases/download/v${VER}"
                f"/chezmoi_${{VER}}_linux_${{ARCH}}.deb -o {_chezmoi_deb}"
            ),
        ],
    )
    apt.deb(
        name="Install chezmoi via deb",
        src=_chezmoi_deb,
        _sudo=True,
    )
    files.file(
        name="Remove chezmoi deb",
        path=_chezmoi_deb,
        present=False,
    )

# The remote source is assembled and uploaded by dotf before PyInfra starts.
# A host can have a server source, shared layers, or both.
if not isinstance(host.connector, LocalConnector):
    _private_repo = os.environ.get("DOTF_REPO", "")
    _server_name = next((group for group in host.groups if group != "all"), None)
    _servers_raw = os.environ.get("DOTF_SERVERS", "")
    _servers = Server.decode_all(_servers_raw) if _servers_raw else []
    _server = next((item for item in _servers if item.name == _server_name), None)

    if _private_repo and _server_name and _server:
        _chezmoi_src = Path(_private_repo) / "chezmoi" / _server_name
        if _chezmoi_src.is_dir() or _server.chezmoi_layers:
            shell(
                name="Apply chezmoi from source dir",
                commands=["chezmoi apply --force --source=/tmp/chezmoi-src"],
            )
