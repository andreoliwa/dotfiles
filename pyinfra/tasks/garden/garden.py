"""Install garden-rs via cargo, then run `garden grow` against ~/.config/garden/garden.yaml.

Prerequisites:

- The `rust` task must have run first - it bootstraps the stable toolchain
  and puts `cargo` in ~/.cargo/bin.
- ~/.config/garden/garden.yaml deployed via chezmoi (private overlay).
"""

from shared import home_path, make_env, shell

_ENV = make_env(home_path(".cargo/bin"))

shell(
    name="cargo install garden-tools",
    commands=["cargo install --quiet --locked garden-tools"],
    _env=_ENV,
)

shell(
    name="garden grow",
    commands=[
        # Use whatever garden config the user has under ~/.config/garden/.
        # Wildcard '*' grows every tree in the config.
        "for cfg in $HOME/.config/garden/*.yaml $HOME/.config/garden/garden.yaml; do "
        '[ -f "$cfg" ] && garden --config "$cfg" grow \'*\' || true; '
        "done",
    ],
    _env=_ENV,
    _ignore_errors=True,
)
