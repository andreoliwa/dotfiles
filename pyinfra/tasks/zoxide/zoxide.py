"""Smart cd replacement. Tracks frecency and jumps to directories with `z`."""

from pyinfra.facts.server import Kernel
from pyinfra.operations import brew, server

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install zoxide",
        packages=["zoxide"],
        latest=True,
    )
else:
    server.shell(
        name="Install zoxide via curl",
        commands=["curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh"],
    )
