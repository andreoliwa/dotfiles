"""Deploy tmux: packages, TPM, and Oh My Tmux cleanup.

~/.tmux.conf is managed by chezmoi (chezmoi/dot_tmux.conf).
"""

from pathlib import Path

from pyinfra.facts.server import Home
from pyinfra.operations import brew, files, git, pipx

from pyinfra import host

HOME = Path(host.get_fact(Home))
TPM_DIR = HOME / ".tmux" / "plugins" / "tpm"
OH_MY_TMUX_DIR = HOME / ".tmux"

# -- packages ------------------------------------------------------------------

brew.packages(
    name="Install tmux",
    packages=["tmux"],
    latest=True,
)


brew.packages(
    name="Install extract_url (needed by tmux-urlview)",
    packages=["extract_url"],
    latest=True,
)

pipx.packages(
    name="Install tmuxp via pipx",
    packages=["tmuxp"],
    latest=True,
)

# -- Oh My Tmux cleanup --------------------------------------------------------
# ~/.tmux/ was the Oh My Tmux git clone; nuke it so chezmoi owns ~/.tmux.conf.

files.directory(
    name="Remove Oh My Tmux (~/.tmux/)",
    path=str(OH_MY_TMUX_DIR),
    present=False,
)

# -- TPM -----------------------------------------------------------------------

git.repo(
    name="Clone or update TPM",
    src="https://github.com/tmux-plugins/tpm",
    dest=str(TPM_DIR),
)
