"""Unified version manager. Uses Homebrew on macOS, curl installer on Linux."""

from pyinfra.facts.server import Kernel
from pyinfra.operations import brew
from shared import shell

from pyinfra import host

if host.get_fact(Kernel) == "Darwin":
    brew.packages(
        name="Install mise",
        packages=["mise"],
        latest=True,
    )
else:
    shell(
        name="Install mise via curl",
        commands=["curl https://mise.run | sh"],
    )
