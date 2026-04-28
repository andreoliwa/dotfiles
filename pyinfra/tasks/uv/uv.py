"""Fast Python package and project manager."""

from pyinfra.facts.server import Kernel
from pyinfra.operations import brew, server

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install uv",
        packages=["uv"],
        latest=True,
    )
else:
    server.shell(
        name="Install uv via curl",
        commands=["curl -LsSf https://astral.sh/uv/install.sh | sh"],
    )
