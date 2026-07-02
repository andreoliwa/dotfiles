"""Dotfiles manager. Installs and applies server-specific chezmoi source.

Remote apply is unconditional here — no diff, no prompt.
The diff preview, rsync, and user confirmation all happen before pyinfra is invoked:
  src/dotf/ops.py :: _chezmoi_remote_diff() rsyncs the source dir to /tmp/chezmoi-src,
  runs `chezmoi diff` there, pipes output through local delta, and prompts.
  Only if confirmed does it call apply_pyinfra(), which eventually includes this file.
  This task then just runs `chezmoi apply --source=/tmp/chezmoi-src`.

For local hosts (@local / macbook), this block is skipped entirely — ops.py handles
local apply via _chezmoi_apply_source() instead.
"""

import os
from pathlib import Path

from pyinfra.connectors.local import LocalConnector
from pyinfra.facts.server import Kernel
from pyinfra.operations import brew
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
    # Install directly from the GitHub release .deb using the dpkg architecture name.
    shell(
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
# For remote hosts, rsync the source dir and apply it with the remote chezmoi.
if not isinstance(host.connector, LocalConnector):
    _private_repo = os.environ.get("DOTF_REPO", "")
    # host.groups contains the inventory variable name (e.g. "rpi").
    # The first non-"all" group is the server name mapping to chezmoi/<server>/.
    _server_name = next((g for g in host.groups if g != "all"), None)

    if _private_repo and _server_name:
        _chezmoi_src = Path(_private_repo) / "chezmoi" / _server_name
        if _chezmoi_src.is_dir():
            # The source dir was already rsynced to /tmp/chezmoi-src by ops.py::_chezmoi_remote_diff
            # before pyinfra was invoked (diff + prompt happen there). Just apply it here.
            # chezmoi diff/apply require the dot_-prefixed source layout, not a rendered archive.
            # --force: pyinfra runs with no TTY, so chezmoi's own "target changed since last
            # write" confirmation prompt cannot render and the apply fails outright. The diff
            # step above already gave the user a chance to review and abort, so skip the
            # redundant (and here, impossible) second confirmation.
            _remote_src_dir = "/tmp/chezmoi-src"  # noqa: S108
            shell(
                name="Apply chezmoi from source dir",
                commands=[f"chezmoi apply --force --source={_remote_src_dir}"],
            )
