"""Bash: login shell setup + completion dir + bash-git-prompt clone.

Brewfile installs bash + bash-completion@2. This task wires the rest:

1. Add /opt/homebrew/bin/bash to /etc/shells (sudo).
2. chsh -s /opt/homebrew/bin/bash.
3. mkdir -p ~/.local/share/bash-completion/completions (BASH_COMPLETION_USER_DIR).
4. Clone https://github.com/magicmonty/bash-git-prompt to ~/.bash-git-prompt.

.bashrc itself is deployed via chezmoi (dotfiles/chezmoi/dot_bashrc).
"""

from pyinfra.facts.server import Kernel
from pyinfra.operations import git, server

from pyinfra import host

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"{_BREW_PATH}:/usr/bin:/bin:/usr/sbin:/sbin"}

if host.get_fact(Kernel) == "Darwin":
    _bash = "/opt/homebrew/bin/bash"

    server.shell(
        name="Register Homebrew bash in /etc/shells",
        commands=[f"grep -qxF '{_bash}' /etc/shells || echo '{_bash}' | sudo tee -a /etc/shells >/dev/null"],
        _env=_ENV,
    )

    server.shell(
        name="chsh to Homebrew bash",
        commands=[f"[ \"$SHELL\" = '{_bash}' ] || chsh -s '{_bash}'"],
        _env=_ENV,
    )

server.shell(
    name="Create BASH_COMPLETION_USER_DIR",
    commands=["mkdir -p $HOME/.local/share/bash-completion/completions"],
    _env=_ENV,
)

git.repo(
    name="Clone bash-git-prompt",
    src="https://github.com/magicmonty/bash-git-prompt.git",
    dest="~/.bash-git-prompt",
    branch="master",
    pull=False,
)
