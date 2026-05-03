"""Caddy web server with caddy-security plugin, built via xcaddy. Linux only."""

from pyinfra.facts.server import Kernel
from pyinfra.operations import apt, server

from pyinfra import host

if host.get_fact(Kernel) == "Linux":
    # xcaddy requires Go — install via the official tarball
    # https://github.com/caddyserver/xcaddy
    apt.packages(
        name="Install xcaddy dependencies",
        packages=["debian-keyring", "debian-archive-keyring", "apt-transport-https"],
        update=True,
    )

    server.shell(
        name="Add Caddy apt repo key",
        commands=[
            "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/xcaddy/gpg.key'"
            " | gpg --dearmor -o /usr/share/keyrings/caddy-xcaddy-archive-keyring.gpg",
        ],
        _sudo=True,
    )

    server.shell(
        name="Add Caddy xcaddy apt source",
        commands=[
            "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/xcaddy/debian.deb.txt'"
            " | tee /etc/apt/sources.list.d/caddy-xcaddy.list",
        ],
        _sudo=True,
    )

    apt.packages(
        name="Install xcaddy",
        packages=["xcaddy"],
        update=True,
        _sudo=True,
    )

    server.shell(
        name="Build Caddy with caddy-security plugin",
        # https://github.com/greenpau/caddy-security
        commands=[
            "xcaddy build --with github.com/greenpau/caddy-security --output /usr/bin/caddy",
        ],
        _sudo=True,
    )

    server.shell(
        name="Enable and start caddy service",
        commands=["systemctl enable --now caddy"],
        _sudo=True,
    )
