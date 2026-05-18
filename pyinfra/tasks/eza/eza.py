"""eza: install via cargo. Shell aliases ship as a shell.d fragment."""

from shared import home_path, make_env, shell

_ENV = make_env(home_path(".cargo/bin"))

shell(
    name="cargo install eza",
    commands=["cargo install --quiet --locked eza"],
    _env=_ENV,
)
