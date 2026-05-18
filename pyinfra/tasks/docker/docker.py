"""Docker: macOS bash completions + OSMC (Raspberry Pi) install.

macOS: OrbStack is the user's preferred Docker runtime; Docker Desktop
completions are linked only if Docker.app is installed. Both targets are
optional - missing source files are silently skipped.

OSMC: installs Docker CE + docker-compose from Docker's official Debian
repo, switches iptables to legacy, adds the osmc user to the docker group.
Reference: https://docs.docker.com/engine/install/debian/
"""

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, server

from pyinfra import host

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"{_BREW_PATH}:/usr/bin:/bin"}

if host.get_fact(Kernel) == "Darwin":
    server.shell(
        name="Link docker.bash-completion if Docker.app present",
        commands=[
            "src=/Applications/Docker.app/Contents/Resources/etc/docker.bash-completion; "
            'dst="$(brew --prefix)/etc/bash_completion.d/docker.bash-completion"; '
            '[ -f "$src" ] && ln -sfn "$src" "$dst" || true',
        ],
        _env=_ENV,
    )
    server.shell(
        name="Link docker-compose.bash-completion if Docker.app present",
        commands=[
            "src=/Applications/Docker.app/Contents/Resources/etc/docker-compose.bash-completion; "
            'dst="$(brew --prefix)/etc/bash_completion.d/docker-compose.bash-completion"; '
            '[ -f "$src" ] && ln -sfn "$src" "$dst" || true',
        ],
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
    server.shell(
        name="Add Docker GPG key",
        commands=[
            "curl -fsSL https://download.docker.com/linux/debian/gpg "
            "| sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
        ],
    )
    server.shell(
        name="Add Docker apt repo",
        commands=[
            'echo "deb [arch=armhf signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] '
            'https://download.docker.com/linux/debian $(lsb_release -cs) stable" '
            "| sudo tee /etc/apt/sources.list.d/docker.list >/dev/null",
        ],
    )
    server.shell(
        name="Revert iptables to legacy",
        commands=[
            "sudo update-alternatives --set iptables /usr/sbin/iptables-legacy "
            "&& sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy",
        ],
    )
    apt.packages(
        name="Install Docker Engine + docker-compose",
        packages=["docker-ce", "docker-ce-cli", "containerd.io", "docker-compose"],
        update=True,
        latest=True,
        _sudo=True,
    )
    server.shell(
        name="Ensure docker group exists",
        commands=["sudo groupadd -f docker"],
    )
    server.shell(
        name="Add osmc user to docker group",
        commands=["sudo usermod -aG docker osmc"],
    )
