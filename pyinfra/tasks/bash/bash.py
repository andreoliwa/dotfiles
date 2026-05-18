"""Bash: login shell setup + completion dir + bash-git-prompt clone.

Brewfile installs bash + bash-completion@2. This task wires the rest:

1. Add /opt/homebrew/bin/bash to /etc/shells (sudo).
2. chsh -s /opt/homebrew/bin/bash.
3. mkdir -p ~/.local/share/bash-completion/completions (BASH_COMPLETION_USER_DIR).
4. Clone https://github.com/magicmonty/bash-git-prompt to ~/.bash-git-prompt.

.bashrc itself is deployed via chezmoi (dotfiles/chezmoi/dot_bashrc).
"""

from pyinfra.facts.server import Kernel
from pyinfra.operations import git
from shared import home_path, make_env, shell

from pyinfra import host

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    _bash = "/opt/homebrew/bin/bash"

    shell(
        name="Register Homebrew bash in /etc/shells",
        commands=[f"grep -qxF '{_bash}' /etc/shells || echo '{_bash}' | sudo tee -a /etc/shells >/dev/null"],
        _env=_ENV,
    )

    shell(
        name="chsh to Homebrew bash",
        commands=[f"[ \"$SHELL\" = '{_bash}' ] || chsh -s '{_bash}'"],
        _env=_ENV,
    )

shell(
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

# complete_alias: bash completion for aliases.
# https://github.com/cykerway/complete-alias
_COMPLETE_ALIAS = home_path(".local/share/bash-completion/completions/complete_alias.bash-completion")
_COMPLETE_ALIASES = (
    # keep-sorted start
    "d",
    "dc",
    "dk",
    "g",
    "ga",
    "gb",
    "gco",
    "gl",
    "gp",
    "gs",
    "gst",
    "i",
    "ih",
    "ir",
    "k",
    "p",
    "rsync-default",
    # keep-sorted end
)
_MARKER = "# === complete_alias: my aliases ==="

shell(
    name="Download complete_alias completion script",
    commands=[
        f"curl -fsSL -o {_COMPLETE_ALIAS} "
        "https://raw.githubusercontent.com/cykerway/complete-alias/master/complete_alias",
    ],
    _env=_ENV,
)

_block = "\\n".join(f"complete -F _complete_alias {a}" for a in _COMPLETE_ALIASES)
shell(
    name="Append my aliases to complete_alias completion",
    commands=[
        f"grep -qF '{_MARKER}' {_COMPLETE_ALIAS} || printf '\\n{_MARKER}\\n{_block}\\n' >> {_COMPLETE_ALIAS}",
    ],
    _env=_ENV,
)
