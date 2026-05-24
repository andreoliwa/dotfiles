"""Kubernetes CLI tools: install via brew, then krew plugins."""

from pyinfra.operations import brew
from shared import home_path, make_env, shell

brew.packages(
    name="Install kubernetes CLI tools",
    packages=["kubectl", "kubernetes-cli", "kubectx", "k9s", "kubie", "krew", "bat"],
    latest=True,
)

_ENV = make_env(home_path(".krew/bin"))

_KREW_PLUGINS = [
    "score",
]

for _plugin in _KREW_PLUGINS:
    shell(
        name=f"kubectl krew install {_plugin}",
        commands=[f"kubectl krew install {_plugin}"],
        _env=_ENV,
        _ignore_errors=True,
    )
