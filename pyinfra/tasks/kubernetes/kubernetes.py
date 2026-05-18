"""Kubernetes CLI: krew plugins. Binaries come from Brewfile."""

from shared import home_path, make_env, shell

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
