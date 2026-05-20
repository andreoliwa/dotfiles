"""Deploy tmux: packages, TPM, and Oh My Tmux cleanup.

Self-contained: only depends on brew CLI (always present after bootstrap.sh)
and git. Can run early in the DAG, before `brew bundle`.

~/.tmux.conf is managed by chezmoi (chezmoi/dot_tmux.conf).
tmuxp is installed via the `uv` task (uv_packages in inventory), not here,
to keep this task free of any pipx/uv dependency.
"""

from pathlib import Path

from pyinfra.facts.server import Home
from pyinfra.operations import brew, files, git

from pyinfra import host

HOME = Path(host.get_fact(Home))
TPM_DIR = HOME / ".tmux" / "plugins" / "tpm"
OH_MY_TMUX_DIR = HOME / ".tmux"

# -- packages ------------------------------------------------------------------

brew.packages(
    name="Install tmux + extract_url (needed by tmux-urlview)",
    packages=["tmux", "extract_url"],
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
