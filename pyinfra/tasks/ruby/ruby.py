"""Ruby: install versions via mise. Versions defined in ~/.config/mise/config.toml."""

from shared import home_path, make_env, shell

_ENV = make_env(home_path(".local/share/mise/shims"))

shell(
    name="mise install ruby",
    commands=["mise install ruby"],
    _env=_ENV,
)
