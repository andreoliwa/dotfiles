# Copyright 2026

"""Bash: install brew bash + completions, then configure shell completion.

Self-contained so it can run before the main `brew bundle` task. On macOS this
allows changing to Homebrew Bash early in provisioning, so new terminals use
Bash and the deployed ~/.config/shell.d/ fragments. On Ubuntu it installs the
system bash-completion package.

macOS:
1. Install bash + bash-completion@2.
2. Register /opt/homebrew/bin/bash in /etc/shells and select it with chsh.
3. Create BASH_COMPLETION_USER_DIR.

.bashrc itself is deployed through chezmoi.
Reference: https://github.com/scop/bash-completion
"""

from pyinfra.facts.server import Kernel, LinuxName
from pyinfra.operations import apt, brew
from shared import home_path, make_env, shell

from pyinfra import host

_ENV = make_env()

if host.get_fact(Kernel) == "Darwin":
    _bash = "/opt/homebrew/bin/bash"

    # Keep this task independent of brew_bundle so a newly provisioned Mac can
    # use Bash and its completions before the rest of its Brewfile is applied.
    brew.packages(
        name="Install bash + bash-completion@2",
        packages=["bash", "bash-completion@2"],
        latest=False,
    )

    shell(
        name="Register Homebrew bash in /etc/shells",
        commands=[f"grep -qxF '{_bash}' /etc/shells || echo '{_bash}' >> /etc/shells"],
        _env=_ENV,
        _sudo=True,
    )

    shell(
        name="chsh to Homebrew bash",
        commands=[f"[ \"$SHELL\" = '{_bash}' ] || chsh -s '{_bash}'"],
        _env=_ENV,
    )
elif host.get_fact(LinuxName) == "Ubuntu":
    apt.packages(
        name="Install bash-completion",
        packages=["bash-completion"],
        update=True,
        _sudo=True,
    )

shell(
    name="Create BASH_COMPLETION_USER_DIR",
    commands=["mkdir -p $HOME/.local/share/bash-completion/completions"],
    _env=_ENV,
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
        (
            f"curl -fsSL -o {_COMPLETE_ALIAS} "
            "https://raw.githubusercontent.com/cykerway/complete-alias/master/complete_alias"
        ),
    ],
    _env=_ENV,
)

_block = "\\n".join(f"complete -F _complete_alias {alias}" for alias in _COMPLETE_ALIASES)
shell(
    name="Append my aliases to complete_alias completion",
    commands=[
        f"grep -qF '{_MARKER}' {_COMPLETE_ALIAS} || printf '\\n{_MARKER}\\n{_block}\\n' >> {_COMPLETE_ALIAS}",
    ],
    _env=_ENV,
)
