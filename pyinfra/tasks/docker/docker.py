# Copyright 2026

"""Docker: macOS completions, Ubuntu packages, and OSMC (Raspberry Pi) install.

macOS: OrbStack is the user's preferred Docker runtime; Docker Desktop
completions are linked only if Docker.app is installed. Both targets are
optional, so missing source files are silently skipped.

OSMC: installs Docker CE + docker-compose from Docker's official Debian repo,
switches iptables to legacy, and adds the osmc user to the docker group.
Reference: https://docs.docker.com/engine/install/debian/
"""

from pyinfra.facts.files import Directory
from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, git, systemd
from shared import home_path, make_env, shell

from pyinfra import host

_ENV = make_env(home_path(".local/bin"))

if host.get_fact(Kernel) == "Darwin":
    shell(
        name="Link docker.bash-completion if Docker.app present",
        commands=[
            (
                "src=/Applications/Docker.app/Contents/Resources/etc/docker.bash-completion; "
                'dst="$(brew --prefix)/etc/bash_completion.d/docker.bash-completion"; '
                '[ -f "$src" ] && ln -sfn "$src" "$dst" || true'
            ),
        ],
        _env=_ENV,
    )
    shell(
        name="Link docker-compose.bash-completion if Docker.app present",
        commands=[
            (
                "src=/Applications/Docker.app/Contents/Resources/etc/docker-compose.bash-completion; "
                'dst="$(brew --prefix)/etc/bash_completion.d/docker-compose.bash-completion"; '
                '[ -f "$src" ] && ln -sfn "$src" "$dst" || true'
            ),
        ],
        _env=_ENV,
    )

# Ubuntu: install Docker packages from the distribution repository.
_DOCKER_STORAGE_DRIVER = host.data.get("docker_storage_driver", "")
_VESSEL_PATH = home_path("dev/me/vessel")

if host.get_fact(LinuxName) == "Ubuntu":
    # Docker CE's containerd.io conflicts with Ubuntu's containerd, which
    # docker.io requires. Remove CE packages first when a host previously used
    # Docker's upstream repository; volumes and images remain on disk.
    apt.packages(
        name="Remove incompatible Docker CE packages",
        packages=[
            "containerd.io",
            "docker-buildx-plugin",
            "docker-ce",
            "docker-ce-cli",
            "docker-ce-rootless-extras",
            "docker-compose-plugin",
        ],
        present=False,
        _sudo=True,
    )
    apt.packages(
        name="Install Docker Engine + docker-compose",
        packages=["docker-compose", "docker-compose-v2", "docker.io"],
        update=True,
        _sudo=True,
    )
    # Only hosts that opt in to a storage-driver migration may change this
    # setting. Other Ubuntu hosts retain their existing Docker data unchanged.
    if _DOCKER_STORAGE_DRIVER:
        shell(
            name=f"Configure Docker {_DOCKER_STORAGE_DRIVER} storage driver",
            commands=[
                (
                    "python3 -c 'import json; from pathlib import Path; "
                    'path = Path("/etc/docker/daemon.json"); '
                    "config = json.loads(path.read_text()) if path.exists() else {}; "
                    f'config["storage-driver"] = "{_DOCKER_STORAGE_DRIVER}"; '
                    "path.parent.mkdir(parents=True, exist_ok=True); "
                    'path.write_text(json.dumps(config, indent=2) + "\\n")\''
                ),
            ],
            _sudo=True,
        )

# Vessel resolves Conjuring from its sibling checkout through ``tool.uv.sources``.
# On Linux servers, refresh both clean Git checkouts so the editable tool cannot
# retain a stale, rsync-synchronized dependency. Local development checkouts are
# left alone to avoid overwriting uncommitted work.
_CONJURING_PATH = home_path("dev/me/conjuring")
_SOURCE_REPOS = (
    ("conjuring", "https://github.com/andreoliwa/conjuring", _CONJURING_PATH),
    ("vessel", "https://github.com/andreoliwa/vessel", _VESSEL_PATH),
)

for _name, _src, _dest in _SOURCE_REPOS:
    if not host.get_fact(Directory, path=_dest):
        git.repo(name=f"Clone {_name}", src=_src, dest=_dest, pull=False)
    elif host.get_fact(LinuxName) == "Ubuntu" and host.get_fact(Directory, path=f"{_dest}/.git"):
        git.repo(name=f"Update {_name}", src=_src, dest=_dest, pull=True)

# Force a rebuild so a changed editable source and its dependencies are used.
shell(
    name="Install vessel as an editable uv tool",
    commands=[f"uv tool install --force -e {_VESSEL_PATH}"],
    _env=_ENV,
)

# OSMC (Raspberry Pi) Docker CE install.
if host.get_fact(LinuxName) == "OSMC":
    apt.packages(
        name="Uninstall old docker versions",
        packages=["docker", "docker-engine", "docker.io", "containerd", "runc"],
        present=False,
        _sudo=True,
    )
    apt.packages(
        name="Install Docker prerequisites",
        packages=[
            "apt-transport-https",
            "ca-certificates",
            "curl",
            "gnupg-agent",
            "software-properties-common",
        ],
        update=True,
        latest=True,
        _sudo=True,
    )
    shell(
        name="Add Docker GPG key",
        commands=[
            (
                "curl -fsSL https://download.docker.com/linux/debian/gpg "
                "| gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
            ),
        ],
        _sudo=True,
    )
    shell(
        name="Add Docker apt repo",
        commands=[
            (
                'echo "deb [arch=armhf signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] '
                'https://download.docker.com/linux/debian $(lsb_release -cs) stable" '
                "> /etc/apt/sources.list.d/docker.list"
            ),
        ],
        _sudo=True,
    )
    shell(
        name="Revert iptables to legacy",
        commands=[
            (
                "update-alternatives --set iptables /usr/sbin/iptables-legacy "
                "&& update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy"
            ),
        ],
        _sudo=True,
    )
    apt.packages(
        name="Install Docker Engine + docker-compose",
        packages=["docker-ce", "docker-ce-cli", "containerd.io", "docker-compose"],
        update=True,
        latest=True,
        _sudo=True,
    )
    shell(
        name="Ensure docker group exists",
        commands=["groupadd -f docker"],
        _sudo=True,
    )
    shell(
        name="Add osmc user to docker group",
        commands=["usermod -aG docker osmc"],
        _sudo=True,
    )

# Docker packages do not reliably start their service after an upgrade or a
# package-source transition. Ensure every Linux Docker target has a daemon now
# and after reboot.
if host.get_fact(Kernel) == "Linux":
    systemd.service(
        name="Enable and start Docker service",
        service="docker",
        running=True,
        enabled=True,
        _sudo=True,
    )
