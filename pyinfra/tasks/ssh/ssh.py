"""SSH client: dirs, known_hosts, and openssl env fragment (macOS only)."""

from pathlib import Path

from lib import DOTFILES_PATH
from pyinfra.facts.server import Kernel
from pyinfra.operations import files, server

from pyinfra import host

_ssh = Path.home() / ".ssh"
ssh_dir = str(_ssh)
config_d = str(_ssh / "config.d")
known_hosts = str(_ssh / "known_hosts")

files.directory(
    name="Ensure ~/.ssh exists",
    path=ssh_dir,
    mode="700",
    present=True,
)

files.directory(
    name="Ensure ~/.ssh/config.d exists",
    path=config_d,
    mode="700",
    present=True,
)

server.shell(
    name="Add GitHub and BitBucket to known_hosts",
    # ssh-keyscan then dedup; avoids repeated entries on re-runs
    commands=[
        f"touch {known_hosts}",
        f"ssh-keyscan -t rsa github.com bitbucket.org 2>/dev/null"
        f" | sort -u - {known_hosts} > {known_hosts}.tmp"
        f" && mv {known_hosts}.tmp {known_hosts}",
    ],
)

if host.get_fact(Kernel) == "Darwin":
    openssl_env = str(DOTFILES_PATH / "pyinfra" / "tasks" / "openssl" / "01-env.sh")
    server.shell(
        name="Regenerate openssl env fragment from brew",
        commands=[
            f"{{ echo '#!/usr/bin/env bash';"
            f" brew info openssl | grep ' export ' | awk '{{$1=$1}};1'; }} > {openssl_env}",
            f"grep -qF DYLD_LIBRARY_PATH {openssl_env}"
            f" || echo 'export DYLD_LIBRARY_PATH=/usr/local/opt/openssl/lib:$DYLD_LIBRARY_PATH'"
            f" >> {openssl_env}",
        ],
    )
