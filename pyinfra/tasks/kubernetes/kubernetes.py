"""Kubernetes CLI: krew plugins. Binaries come from Brewfile."""

from constants import make_env
from pyinfra.operations import server

_ENV = make_env("$HOME/.krew/bin")

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
