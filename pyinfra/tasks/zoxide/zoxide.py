# Copyright 2026

"""Smart cd replacement. Tracks frecency and jumps to directories with `z`."""

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, brew
from shared import shell

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install zoxide",
        packages=["zoxide"],
        latest=True,
    )
elif host.get_fact(LinuxName) == "Ubuntu":
    apt.packages(
        name="Install zoxide",
        packages=["zoxide"],
        update=True,
        _sudo=True,
    )
else:
    shell(
        name="Install zoxide via curl",
        commands=["curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh"],
    )
