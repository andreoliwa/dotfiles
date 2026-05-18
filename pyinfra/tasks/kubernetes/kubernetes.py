"""Kubernetes CLI: krew plugins. Binaries come from Brewfile."""

from pyinfra.operations import server

_BREW_PATH = "/opt/homebrew/bin:/usr/local/bin:/home/linuxbrew/.linuxbrew/bin"
_ENV = {"PATH": f"$HOME/.krew/bin:{_BREW_PATH}:/usr/bin:/bin"}

_KREW_PLUGINS = [
    "score",
]

for _plugin in _KREW_PLUGINS:
    server.shell(
        name=f"kubectl krew install {_plugin}",
        commands=[f"kubectl krew install {_plugin}"],
        _env=_ENV,
        _ignore_errors=True,
    )
