"""Java: install versions via mise. Versions defined in ~/.config/mise/config.toml."""

from shared import home_path, make_env, shell

_ENV = make_env(home_path(".local/share/mise/shims"))

shell(
    name="mise install java",
    commands=["mise install java"],
    _env=_ENV,
)
