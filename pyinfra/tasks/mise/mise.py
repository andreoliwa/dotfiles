"""Deploy mise: install via Homebrew."""

from pyinfra.operations import brew

brew.packages(
    name="Install mise",
    packages=["mise"],
    latest=True,
)
