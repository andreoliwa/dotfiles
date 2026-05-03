"""Caddy web server with caddy-security plugin, built via xcaddy. Linux only."""

from pathlib import Path

from pyinfra.facts.server import Kernel
from pyinfra.operations import apt, files, server

from pyinfra import host

if host.get_fact(Kernel) == "Linux":
    # xcaddy requires Go — install via the official tarball
    # https://github.com/caddyserver/xcaddy

    # Key and source must be set up before any apt-get update — the xcaddy repo key expires
    # periodically, and if the source is already configured on the host, apt-get update will
    # fail signature verification before we get a chance to refresh the key.
    server.shell(
        name="Add Caddy xcaddy apt source",
        commands=[
            "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/xcaddy/debian.deb.txt'"
            " | tee /etc/apt/sources.list.d/caddy-xcaddy.list",
        ],
        _sudo=True,
    )

    server.shell(
        name="Refresh Caddy apt repo key",
        commands=[
            "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/xcaddy/gpg.key'"
            " | gpg --batch --yes --dearmor -o /usr/share/keyrings/caddy-xcaddy-archive-keyring.gpg",
        ],
        _sudo=True,
    )

    apt.packages(
        name="Install xcaddy dependencies",
        packages=["debian-keyring", "debian-archive-keyring", "apt-transport-https"],
        update=True,
    )

    apt.packages(
        name="Install xcaddy",
        packages=["xcaddy"],
        _sudo=True,
    )

    server.shell(
        name="Build Caddy with caddy-security plugin",
        # https://github.com/greenpau/caddy-security
        # /usr/local/go/bin is not in the non-interactive SSH PATH — use full path via GOROOT.
        commands=[
            "PATH=$PATH:/usr/local/go/bin"
            " xcaddy build --with github.com/greenpau/caddy-security --output /usr/bin/caddy",
        ],
        _sudo=True,
    )

    # Override the systemd unit to read the Caddyfile from ~/.config/caddy/ instead of
    # /etc/caddy/Caddyfile so chezmoi can manage it (chezmoi only manages files under ~).
    files.directory(
        name="Create caddy systemd drop-in dir",
        path="/etc/systemd/system/caddy.service.d",
        _sudo=True,
    )

    files.put(
        name="Install caddy systemd drop-in",
        src=str(Path(__file__).parent / "caddy-config-path.conf"),
        dest="/etc/systemd/system/caddy.service.d/config-path.conf",
        _sudo=True,
    )

    server.shell(
        name="Reload systemd and enable caddy",
        commands=[
            "systemctl daemon-reload",
            "systemctl enable caddy",
        ],
        _sudo=True,
    )

    server.shell(
        name="Restart caddy",
        commands=["systemctl restart caddy"],
        _sudo=True,
        _ignore_errors=True,
    )
