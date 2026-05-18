"""Poetry bash completion. Poetry itself is installed by mise."""

from shared import home_path, make_env, shell

_ENV = make_env(home_path(".local/share/mise/shims"))

shell(
    name="Remove legacy ~/.poetry dir",
    commands=["rm -rf $HOME/.poetry"],
    _env=_ENV,
    _ignore_errors=True,
)

shell(
    name="poetry bash completion",
    commands=[
        "mkdir -p $HOME/.local/share/bash-completion/completions && "
        "poetry completions bash > $HOME/.local/share/bash-completion/completions/poetry.bash-completion",
    ],
    _env=_ENV,
    _ignore_errors=True,
)
